"""전체 출력 / rg / Context Mode 실제 CLI 비교. 토큰·정확도 일반 보장으로 해석하지 않는다."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import time
from context_mode_fixtures import document, QUESTIONS

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("context_search", ROOT / "skills/diagnosing-bugs/scripts/context_search.py")
helper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helper)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--runtime", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    a.out.mkdir(parents=True, exist_ok=False)
    file = a.out / "handbook.md"
    file.write_text(document(), encoding="utf-8")
    records = []
    for name, case in QUESTIONS.items():
        raw = file.read_text(encoding="utf-8")
        start = time.perf_counter()
        if shutil.which("rg"):
            rg = subprocess.run([shutil.which("rg"), "-n", "-A", "3", "Orchid API retry contract|Cedar migration consumer contract", str(file)], capture_output=True, text=True, encoding="utf-8", check=True).stdout
            baseline_tool = "rg"
        else:
            lines = raw.splitlines()
            rg = "\n".join("\n".join(lines[i:i+4]) for i, line in enumerate(lines) if "Orchid API retry contract" in line or "Cedar migration consumer contract" in line)
            baseline_tool = "python line filter (rg unavailable)"
        rg_ms = (time.perf_counter() - start) * 1000
        start = time.perf_counter()
        result = helper.search(file, [case["query"]], a.runtime.resolve(), a.out / "cache", 2)
        cold_ms = (time.perf_counter() - start) * 1000
        text = json.dumps(result, ensure_ascii=False)
        start = time.perf_counter()
        repeated = helper.search(file, [case["query"]], a.runtime.resolve(), a.out / "cache", 2)
        warm_ms = (time.perf_counter() - start) * 1000
        records.append({"case": name, "baseline_tool": baseline_tool, "raw_utf8_bytes": len(raw.encode()), "rg_utf8_bytes": len(rg.encode()),
                        "context_utf8_bytes": len(text.encode()), "rg_ms": round(rg_ms, 2),
                        "context_first_ms": round(cold_ms, 2), "context_repeat_ms": round(warm_ms, 2),
                        "context_reused_at_start": result["cache_reused"], "repeat_reused": repeated["cache_reused"],
                        "raw_facts": all(n in raw.lower() for n in case["needles"]),
                        "rg_facts": all(n in rg.lower() for n in case["needles"]),
                        "context_facts": all(n in text.lower() for n in case["needles"])})
    before = hashlib.sha256(file.read_bytes()).hexdigest()
    file.write_text(document().replace("four total attempts", "six total attempts"), encoding="utf-8")
    changed = helper.search(file, [QUESTIONS["retry"]["query"]], a.runtime.resolve(), a.out / "cache", 2)
    changed_ok = not changed["cache_reused"] and "six total attempts" in json.dumps(changed) and changed["sha256"] != before
    other = a.out / "other.md"
    other.write_text("# Other project\nBanana-only reference; no shared operational policy.", encoding="utf-8")
    isolated = helper.search(other, ["Orchid retry"], a.runtime.resolve(), a.out / "cache", 2)
    isolated_ok = "Orchid API retry contract" not in json.dumps(isolated)
    korean = helper.search(file, ["결제 취소"], a.runtime.resolve(), a.out / "cache", 2)
    korean_ok = "영수증" in json.dumps(korean, ensure_ascii=False)
    result = {"scope": "synthetic documented CLI retrieval; UTF-8 output bytes, not billed tokens; rg uses known exact headings", "cases": records,
              "changed_input_refreshed": changed_ok, "other_file_isolated": isolated_ok, "korean_exact_query": korean_ok,
              "passed": all(c["context_facts"] and c["rg_facts"] and c["repeat_reused"] for c in records) and changed_ok and isolated_ok and korean_ok}
    (a.out / "summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(not result["passed"])


if __name__ == "__main__":
    main()
