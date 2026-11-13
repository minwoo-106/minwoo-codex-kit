"""문서 안내의 실제 읽기·범위 선택 시험. 기본은 계획만 출력한다."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from run_routing import grade

CASES = [
    ('new-report', 'A4 내부 주간 업무 PDF를 새로 만들려고 해. 샘플 운영팀의 자료 정리 12건 중 10건 완료, 2건은 확인 중이야. 다음 주 목표일은 내부 계획이고 외부 확약은 아니야. 별도 회사 양식은 없고 읽기 편한 업무 문서가 목적이야.'),
    ('fixed-template', '지정 양식의 내부 업무 PDF를 개편하려 해. 양식은 파란 제목, 로고, 결재란, 하단의 8pt 필수 고지를 유지해야 해. 문구의 반복과 읽기 흐름만 자연스럽게 정리하려고 해. 필수 고지는 외부 일정이 미확정이라는 내용이야.'),
    ('extract-only', 'PDF에서 날짜와 합계 값만 그대로 추출하려고 해. 문체·디자인 변경이나 새 문서 제작은 원하지 않아.'),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--out', type=Path)
    parser.add_argument('--skills-root', type=Path)
    parser.add_argument('--pdf-skill', type=Path)
    args = parser.parse_args()
    if not args.run:
        print(json.dumps({'cases': [name for name, _ in CASES], 'mode': 'plan; no model calls'}))
        return
    if not all((args.out, args.skills_root, args.pdf_skill, shutil.which('codex'))):
        parser.error('--run requires installed Codex, --out, --skills-root and --pdf-skill')
    out = args.out.resolve()
    repo = Path(__file__).resolve().parent.parent
    if out == repo or repo in out.parents:
        parser.error('raw traces must remain outside the public repository')
    out.mkdir(parents=True, exist_ok=False)
    ref = args.skills_root / 'minwoo-skill-curation/references'
    docs = {name: (ref / name).read_text(encoding='utf-8') for name in [
        'routing.md', 'routing/documents.md', 'routing/document-quality.md', 'routing/document-candidates.md']}
    docs['pdf'] = args.pdf_skill.read_text(encoding='utf-8')
    results = []
    for name, request in CASES:
        project = out / name
        project.mkdir()
        marker = project / 'README.md'
        marker.write_text('Synthetic preparation test. No real files or service data.\n', encoding='utf-8')
        before = {p.relative_to(project).as_posix(): p.read_bytes() for p in project.rglob('*') if p.is_file()}
        prompt = request + '\n이번에는 실제 파일 제작·추출 전 읽기 전용 준비만 해. 필요한 지침을 실제로 읽고, 어떤 형식 도구로 무엇을 유지하거나 바꿀지 짧게 설명해. 파일 쓰기·생성·설치·웹 검색·외부 서비스 호출은 하지 마. 원본 파일 요청 대신 주어진 조건에서 준비 판단만 해.'
        prompt += '\n이 시험 환경의 PDF 형식 지침 위치: ' + str(args.pdf_skill.resolve())
        command = [shutil.which('codex'), 'exec', '--ephemeral', '--json', '--sandbox', 'read-only', '--skip-git-repo-check', '-C', str(project), '-']
        print('START ' + name, flush=True)
        try:
            proc = subprocess.run(command, input=prompt, text=True, encoding='utf-8', capture_output=True, timeout=300)
        except subprocess.TimeoutExpired as exc:
            decode = lambda value: value.decode('utf-8', errors='replace') if isinstance(value, bytes) else (value or '')
            proc = subprocess.CompletedProcess(command, 124, decode(exc.stdout), decode(exc.stderr))
        (out / (name + '-trace.jsonl')).write_text(proc.stdout, encoding='utf-8')
        (out / (name + '-stderr.txt')).write_text(proc.stderr, encoding='utf-8')
        events, malformed = [], False
        for line in proc.stdout.splitlines():
            try:
                events.append(json.loads(line))
            except ValueError:
                malformed = True
        expected = ['routing/documents.md', 'routing/document-quality.md'] if name != 'extract-only' else []
        case = {'routes': expected, 'expected': ['pdf'], 'allowed': ['pdf'],
                'allowed_routes': ['routing.md'] if expected else []}
        result = grade(events, docs, case)
        after = {p.relative_to(project).as_posix(): p.read_bytes() for p in project.rglob('*') if p.is_file()}
        result.update(id=name, exit_code=proc.returncode, fixture_unchanged=before == after,
                      trace_sha256=hashlib.sha256(proc.stdout.encode()).hexdigest())
        result['passed'] &= proc.returncode == 0 and before == after and not malformed
        messages = '\n'.join(e['item'].get('text', '') for e in events if e.get('type') == 'item.completed' and e['item'].get('type') == 'agent_message')
        (out / (name + '-messages.md')).write_text(messages, encoding='utf-8')
        results.append(result)
        (out / 'summary.json').write_text(json.dumps({'scope': 'read-only guide selection; substantive decisions need manual review', 'results': results}, ensure_ascii=False, indent=2), encoding='utf-8')
        print(('PASS ' if result['passed'] else 'FAIL ') + name, flush=True)
    raise SystemExit(0 if all(r['passed'] for r in results) else 1)


if __name__ == '__main__':
    main()
