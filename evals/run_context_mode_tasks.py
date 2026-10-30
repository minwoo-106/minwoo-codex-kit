"""동일한 두 실전 과제를 기존 검색/Context Mode로 각각 수행. 기본값은 실행 없는 계획."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
from context_mode_fixtures import QUESTIONS, create, acceptance

ROOT = Path(__file__).resolve().parents[1]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run", action="store_true")
    p.add_argument("--out", type=Path)
    p.add_argument("--runtime", type=Path)
    p.add_argument("--mode", choices=["baseline", "context"])
    a = p.parse_args()
    modes = [a.mode] if a.mode else ["baseline", "context"]
    if not a.run:
        print(json.dumps({"cases": list(QUESTIONS), "modes": modes, "run": False}))
        return
    if not a.out or not a.runtime:
        p.error("--out --runtime 필요")
    out = a.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    helper = ROOT / "skills/diagnosing-bugs/scripts/context_search.py"
    results = []
    for mode in modes:
        for case, task in QUESTIONS.items():
            folder = out / (mode + "-" + case)
            create(folder)
            digest = hashlib.sha256((folder / "handbook.md").read_bytes()).hexdigest()
            method = ("기존 파일/터미널 검색 도구로 필요한 부분을 찾아. Context Mode는 이번 비교군에서는 사용하지 마." if mode == "baseline" else
                f"문서 탐색은 Context Mode 검색 도구로 먼저 해. 실행기: {helper}\n런타임: {a.runtime.resolve()}\n"
                "사용법: python <실행기> --runtime <런타임> --file handbook.md --query '검색어' --cache-root .context-cache\n"
                "결과는 500자 검색 조각이므로 original_sections가 알려주는 필요한 원문 행 범위/예외를 일반 파일 도구로 확인한 후 결론을 내려. 넓은 키워드로 문서 전체를 다시 출력하지 마. 적용 지침은 이 검색 도구로 읽지 마.")
            prompt = (task["prompt"] + "\n" + method +
                "\n합성 평가 프로젝트 안에서 요청된 작업은 승인돼 있어. 다른 프로젝트·설정·승인 방식·네트워크·GitHub는 변경하지 마. "
                "테스트만 통과시키기 위한 가짜 동작 없이 작업하고 실제 결과만 짧게 보고해.")
            print("START " + mode + " " + case, flush=True)
            started = time.monotonic()
            try:
                proc = subprocess.run([shutil.which("codex") or "codex", "exec", "--ephemeral", "--json", "--sandbox", "workspace-write", "--skip-git-repo-check", "-C", str(folder), "-"],
                    input=prompt, capture_output=True, encoding="utf-8", timeout=360,
                    env={**os.environ, "PYTHONUTF8": "1", "PYTHONDONTWRITEBYTECODE": "1"})
                raw, error, code = proc.stdout, proc.stderr, proc.returncode
            except subprocess.TimeoutExpired as exc:
                raw, error, code = exc.stdout or b"", exc.stderr or b"", 124
                if isinstance(raw, bytes): raw = raw.decode("utf-8", errors="replace")
                if isinstance(error, bytes): error = error.decode("utf-8", errors="replace")
            (out / (mode + "-" + case + ".jsonl")).write_text(raw, encoding="utf-8")
            (out / (mode + "-" + case + ".stderr")).write_text(error, encoding="utf-8")
            events = []
            for line in raw.splitlines():
                try: events.append(json.loads(line))
                except ValueError: pass
            commands = [e["item"] for e in events if e.get("type") == "item.completed" and e.get("item", {}).get("type") == "command_execution"]
            finished = [e for e in events if e.get("type") == "turn.completed"]
            used = any("context_search.py" in c.get("command", "") and c.get("exit_code") == 0 for c in commands)
            original_checked = any(c.get("exit_code") == 0 and "handbook.md" in c.get("command", "") and "context_search.py" not in c.get("command", "") and
                                   ("four total attempts" in c.get("aggregated_output", "") if case == "retry" else "at least 30 days" in c.get("aggregated_output", "")) for c in commands)
            try: correct = acceptance(case, folder)
            except (OSError, ValueError, subprocess.SubprocessError): correct = False
            preserved = digest == hashlib.sha256((folder / "handbook.md").read_bytes()).hexdigest()
            result = {"mode": mode, "case": case, "passed": code == 0 and bool(finished) and correct and preserved and original_checked and used == (mode == "context"),
                      "artifact_correct": correct, "original_preserved": preserved, "original_section_read": original_checked,
                      "context_command_succeeded": used, "exit_code": code, "seconds": round(time.monotonic() - started, 2),
                      "command_output_utf8_bytes": sum(len(c.get("aggregated_output", "").encode()) for c in commands),
                      "usage": finished[-1].get("usage", {}) if finished else {},
                      "trace_sha256": hashlib.sha256(raw.encode()).hexdigest()}
            results.append(result)
            (out / "summary.json").write_text(json.dumps({"scope": "two synthetic native Codex tasks per method; explicit method, one run each; not a general performance benchmark", "results": results}, ensure_ascii=False, indent=2), encoding="utf-8")
            print(json.dumps(result, ensure_ascii=False), flush=True)
    raise SystemExit(not all(r["passed"] for r in results))


if __name__ == "__main__":
    main()
