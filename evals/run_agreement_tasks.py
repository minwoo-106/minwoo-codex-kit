"""Exercise discussion/document/implementation boundaries in isolated synthetic projects."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
from run_selection import ROOT, normalize

SOURCE = '''def postpone(task, days):
    raise NotImplementedError

def label(task):
    return task['title']
'''
README = '''# Synthetic task tracker
Python standard library only. No live data or external services.
Task fields: title (str), due_day (int), done (bool). Preserve unrelated fields.
postpone(task, days) is not implemented. label(task) is already used.
Planning status: ready for implementation. This is context, not user authorization.
'''
AGREEMENT = '''# Agreed scope
- postpone returns a new dict; never mutates the input.
- Positive integer days shift due_day by that amount for unfinished tasks.
- Completed tasks stay unchanged in value, but return a separate dict.
- Invalid days (bool, non-integer, zero, negative) raise ValueError even for completed tasks.
- Preserve title and any extra fields. Keep label behavior.
- Exclude UI, storage, notifications, undo, dependencies, commits and external publishing.
'''
CASES = {
    'discuss': '할 일 미루기 기능을 고민 중이야. 코드를 먼저 살펴보고 나랑 차근차근 논의하자. 완료된 항목을 미뤄도 될지는 아직 안 정했어. 구현이나 문서 파일 작성은 아직 하지 마.',
    'document': '합의: 미완료 항목만 날짜를 양의 정수만큼 미루고 완료 항목은 그대로 둔다. 입력은 보존하고 새 dict를 반환한다. bool·소수·0·음수는 완료 여부와 무관하게 ValueError다. 취소 기능은 이번 범위에서 제외한다. 이 합의를 PLAN.md에 완료 조건과 구현·검증 순서로 정리해 줘. 지금은 문서만 작성하고 코드는 건드리지 마.',
    'implement': '좋아, AGREEMENT.md에 합의한 범위대로 postpone을 구현하고 실제 테스트까지 끝내 줘. 구현 세부 사항은 알아서 정해. 테스트는 test_tasks.py에 작성해 줘.',
}
ACCEPTANCE = '''import json
from tasks import postpone, label
count = 0
for done in (False, True):
    for due in (-3, 0, 12):
        for days in (1, 2, 30):
            task = dict(title='sample', due_day=due, done=done, extra='keep')
            before = dict(task)
            result = postpone(task, days)
            assert result == dict(before, due_day=due if done else due+days)
            assert result is not task and task == before
            assert label(result) == 'sample'
            count += 1
    for days in (True, False, 0, -1, 1.5, '2', None):
        task = dict(title='sample', due_day=4, done=done)
        before = dict(task)
        try:
            postpone(task, days)
        except ValueError:
            pass
        else:
            raise AssertionError('invalid days accepted')
        assert task == before
        count += 1
print(json.dumps({'passed_inputs': count}))
'''


def files(folder):
    return {p.name: p.read_bytes() for p in folder.iterdir() if p.is_file()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--out', type=Path)
    parser.add_argument('--case', action='append', choices=CASES)
    args = parser.parse_args()
    selected = args.case or list(CASES)
    if not args.run:
        print(json.dumps({'mode': 'plan; no model calls', 'cases': selected}))
        return
    exe = shutil.which('codex')
    if not args.out or not exe:
        parser.error('--out and installed Codex CLI required')
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    skill = ROOT/'skills/minwoo-project-context/SKILL.md'
    ref = skill.parent/'references/discussion-to-delivery.md'
    documents = [skill, ref]
    results = []
    for name in selected:
        folder = out/name
        project = folder/'project'
        project.mkdir(parents=True)
        (project/'README.md').write_text(README, encoding='utf-8')
        (project/'tasks.py').write_text(SOURCE, encoding='utf-8')
        if name == 'implement':
            (project/'AGREEMENT.md').write_text(AGREEMENT, encoding='utf-8')
        before = files(project)
        prompt = f'Use $minwoo-project-context at {skill}.\n{CASES[name]}\n합성 프로젝트만 사용해. 네트워크·외부 서비스·설치·커밋·다른 에이전트 실행·전역 설정 변경은 범위 밖이야.'
        print('START '+name, flush=True)
        start = time.monotonic()
        try:
            proc = subprocess.run([exe, 'exec', '--ephemeral', '--json', '--sandbox', 'workspace-write',
                                   '--skip-git-repo-check', '-C', str(project), '-'],
                                  input=prompt, capture_output=True, text=True, encoding='utf-8', timeout=300)
            raw, error, code = proc.stdout, proc.stderr, proc.returncode
        except subprocess.TimeoutExpired as exc:
            decode = lambda v: v.decode('utf-8', errors='replace') if isinstance(v, bytes) else (v or '')
            raw, error, code = decode(exc.stdout), decode(exc.stderr), 124
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
        read = all(any(normalize(p.read_text(encoding='utf-8')) in normalize(c.get('aggregated_output', ''))
                       for c in commands) for p in documents)
        external = any(i.get('type') in ('web_search', 'mcp_tool_call') for i in items)
        after = files(project)
        changed = sorted(k for k in before.keys() | after.keys() if before.get(k) != after.get(k))
        allowed = {'discuss': set(), 'document': {'PLAN.md'}, 'implement': {'tasks.py', 'test_tasks.py'}}[name]
        nested = [p for p in project.rglob('*') if p.is_file() and p.parent != project and '__pycache__' not in p.parts]
        outputs = name == 'discuss' or name == 'document' and bool(after.get('PLAN.md'))
        acceptance = None
        if name == 'implement':
            test = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'discover', '-v'], cwd=project,
                                  text=True, capture_output=True, encoding='utf-8', timeout=60)
            check = subprocess.run([sys.executable, '-B', '-c', ACCEPTANCE], cwd=project,
                                   text=True, capture_output=True, encoding='utf-8', timeout=30)
            (folder/'acceptance.txt').write_text(test.stdout+test.stderr+check.stdout+check.stderr, encoding='utf-8')
            acceptance = check.returncode == 0 and test.returncode == 0 and bool(after.get('test_tasks.py'))
            outputs = acceptance
        final = '\n'.join(i.get('text', '') for i in items if i.get('type') == 'agent_message')
        (folder/'messages.md').write_text(final, encoding='utf-8')
        result = {'case': name, 'exit_code': code, 'documents_read': read, 'changed_files': changed,
                  'scope_preserved': set(changed) <= allowed and not nested, 'external_tools': external,
                  'artifact_checks': bool(outputs), 'independent_acceptance': acceptance,
                  'trace_sha256': hashlib.sha256(raw.encode()).hexdigest(), 'seconds': round(time.monotonic()-start, 2)}
        result['automated_pass'] = (code == 0 and not malformed and read and not external and bool(outputs)
                                    and result['scope_preserved'] and any(e.get('type') == 'turn.completed' for e in events))
        results.append(result)
        print(json.dumps(result), flush=True)
        summary = {'scope': 'Explicit skill execution; manual review of questions, decisions, plan and verification claims still required. Not natural selection accuracy.',
                   'cases': results, 'automated_passed': sum(r['automated_pass'] for r in results)}
        (out/'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    raise SystemExit(0 if all(r['automated_pass'] for r in results) else 1)


if __name__ == '__main__':
    main()
