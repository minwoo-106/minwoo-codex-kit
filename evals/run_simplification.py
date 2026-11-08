"""Paired real Codex trials. Defaults to plan; raw traces remain in a private fresh directory."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

from run_selection import ROOT
from simplification_fixtures import CASES, seed

DOCUMENTS = ['global/AGENTS.md',
             'skills/minwoo-skill-curation/references/routing/refactoring.md',
             'skills/minwoo-test-quality/references/metrics-and-mutations.md']


def documents_read(documents, commands):
    # PowerShell can return CRCRLF when a CRLF snapshot is written in text mode.
    # Line-oriented Get-Content can also expand the extra CR into empty lines.
    # Retain every nonempty line, its indentation, content and order.
    normalize = lambda text: '\n'.join(line for line in text.replace('\r', '').split('\n') if line)
    return all(any(c.get('exit_code') == 0 and normalize(content) in normalize(c.get('aggregated_output', ''))
                   for c in commands) for content in documents)


def files(folder):
    return {p.relative_to(folder).as_posix(): p.read_bytes() for p in folder.rglob('*')
            if p.is_file() and '__pycache__' not in p.parts}


def metrics(folder):
    result = {'production_nonblank_lines': 0, 'test_nonblank_lines': 0, 'branches': 0, 'imports': []}
    imports = set()
    for p in folder.rglob('*.py'):
        source = p.read_text(encoding='utf-8-sig')
        test = p.name.startswith('test_')
        result['test_nonblank_lines' if test else 'production_nonblank_lines'] += sum(bool(s.strip()) for s in source.splitlines())
        if test:
            continue
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, (ast.If, ast.IfExp, ast.For, ast.While, ast.ExceptHandler, ast.comprehension)):
                result['branches'] += 1
            if isinstance(node, ast.Import):
                imports.update(a.name for a in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.add(node.module or '')
    result['imports'] = sorted(imports)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--before-ref', default='6e4b899d4070a266ef20416ad09aae90b8ba48a3')
    parser.add_argument('--out', type=Path)
    parser.add_argument('--case', action='append', choices=CASES)
    args = parser.parse_args()
    selected = args.case or list(CASES)
    if not args.run:
        print(json.dumps({'mode': 'plan; no model calls', 'cases': selected, 'arms': ['before', 'after']}))
        return
    exe = shutil.which('codex')
    if not exe or not args.out:
        parser.error('installed Codex and --out required')
    out = args.out.resolve()
    if out == ROOT or ROOT in out.parents:
        parser.error('raw evaluation output must be outside the repository')
    out.mkdir(parents=True, exist_ok=False)
    snapshots = {}
    for arm in ('before', 'after'):
        snapshots[arm] = {}
        for relative in DOCUMENTS:
            content = (subprocess.check_output(['git', 'show', args.before_ref+':'+relative], cwd=ROOT)
                       if arm == 'before' else (ROOT/relative).read_bytes())
            snapshots[arm][relative] = content.decode('utf-8-sig').replace('\r\n', '\n')
    results = []
    for index, name in enumerate(selected):
        for arm in (('before', 'after') if index % 2 == 0 else ('after', 'before')):
            folder = out/(name+'-'+arm)
            project = folder/'project'
            project.mkdir(parents=True)
            seed(project, name)
            for relative, content in snapshots[arm].items():
                filename = 'AGENTS.md' if relative == DOCUMENTS[0] else Path(relative).name
                (project/filename).write_text(content, encoding='utf-8', newline='\n')
            before = files(project)
            initial_metrics = metrics(project)
            prompt = ('합성 프로젝트의 AGENTS.md, refactoring.md, metrics-and-mutations.md를 모두 읽고 적용해.\n'
                      + CASES[name]['request'] + '\n'
                      '기존 test_existing.py는 보존하고 추가 테스트는 test_changes.py에 작성해. '
                      '외부 자료·다른 프로젝트·스킬 문서·다른 에이전트는 읽거나 호출하지 마. '
                      '이 폴더의 app.py와 test_changes.py만 수정하고 Python 표준 라이브러리만 사용해. '
                      '네트워크·설치·커밋·외부 서비스·전역 설정 변경은 범위 밖이야. 실제 테스트를 실행해.')
            print('START '+name+' '+arm, flush=True)
            start = time.monotonic()
            try:
                proc = subprocess.run([exe, 'exec', '--ephemeral', '--json', '--sandbox', 'workspace-write',
                                       '--skip-git-repo-check', '-C', str(project), '-'], input=prompt,
                                      text=True, capture_output=True, encoding='utf-8', timeout=360)
                raw, error, code = proc.stdout, proc.stderr, proc.returncode
            except subprocess.TimeoutExpired as exc:
                decode = lambda v: v.decode('utf-8', errors='replace') if isinstance(v, bytes) else (v or '')
                raw, error, code = decode(exc.stdout), decode(exc.stderr), 124
            seconds = round(time.monotonic()-start, 2)
            (folder/'trace.jsonl').write_text(raw, encoding='utf-8')
            (folder/'stderr.txt').write_text(error, encoding='utf-8')
            events = []
            malformed = False
            for line in raw.splitlines():
                try:
                    events.append(json.loads(line))
                except ValueError:
                    malformed = True
            items = [e['item'] for e in events if e.get('type') == 'item.completed']
            commands = [i for i in items if i.get('type') == 'command_execution' and i.get('exit_code') == 0]
            read = documents_read(snapshots[arm].values(), commands)
            after = files(project)
            changed = sorted(k for k in before.keys() | after.keys() if before.get(k) != after.get(k))
            scope = set(changed) <= {'app.py', 'test_changes.py'}
            test = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover', '-v'], cwd=project,
                                  capture_output=True, text=True, encoding='utf-8', timeout=60)
            acceptance = subprocess.run([sys.executable, '-B', str(ROOT/'evals/simplification_fixtures.py'), name, str(project)],
                                        capture_output=True, text=True, encoding='utf-8', timeout=30)
            (folder/'acceptance.txt').write_text(test.stdout+test.stderr+acceptance.stdout+acceptance.stderr, encoding='utf-8')
            messages = '\n'.join(i.get('text', '') for i in items if i.get('type') == 'agent_message')
            (folder/'messages.md').write_text(messages, encoding='utf-8')
            passed_inputs = None
            if acceptance.returncode == 0:
                passed_inputs = json.loads(acceptance.stdout)['passed_inputs']
            try:
                final_metrics = metrics(project)
            except (SyntaxError, UnicodeError):
                final_metrics = None
            result = {'case': name, 'arm': arm, 'exit_code': code, 'documents_read': read,
                      'scope_preserved': scope, 'changed_files': changed,
                      'external_tools': any(i.get('type') in ('web_search', 'mcp_tool_call') for i in items),
                      'tests_passed': test.returncode == 0 and bool(after.get('test_changes.py')),
                      'passed_inputs': passed_inputs, 'initial_metrics': initial_metrics,
                      'final_metrics': final_metrics, 'seconds': seconds,
                      'trace_sha256': hashlib.sha256(raw.encode()).hexdigest(),
                      'instruction_sha256': {k: hashlib.sha256(v.encode()).hexdigest() for k, v in snapshots[arm].items()},
                      'usage': [e.get('usage') for e in events if e.get('type') == 'turn.completed']}
            result['automated_pass'] = (code == 0 and not malformed and read and scope and not result['external_tools']
                                        and result['tests_passed'] and bool(passed_inputs) and bool(result['usage']))
            results.append(result)
            print(json.dumps(result), flush=True)
            summary = {'before_ref': args.before_ref, 'scope': 'Explicit instruction loading; 3 synthetic task types, one trial per arm. Not natural selection accuracy or a speed benchmark. Manual trace and readability review required.', 'cases': results}
            (out/'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    raise SystemExit(0 if all(r['automated_pass'] for r in results) else 1)


if __name__ == '__main__':
    main()
