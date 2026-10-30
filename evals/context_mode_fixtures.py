"""Context Mode와 기존 검색을 비교하는 공개 합성 자료. 실제 개인 로그 없음."""
from pathlib import Path

QUESTIONS = {
    "retry": {"query": "Orchid retry idempotency budget", "needles": ["429", "503", "four", "idempotency", "validation"],
              "prompt": "app.py의 should_retry(status, attempt, keyed)를 handbook.md의 Orchid API 규약에 맞게 고쳐. attempt는 이미 완료된 호출 횟수야. 기존 함수 이름과 인자를 유지하고 unittest로 검증해. 문서는 수정하지 마."},
    "migration": {"query": "Cedar migration customer_id rollback index", "needles": ["customer_id", "account_ref", "concurrently", "drop", "30"],
                  "prompt": "handbook.md의 Cedar migration에서 기존 응답 키, 추가 응답 키, 두 키를 함께 유지할 최소 일수, 인덱스 생성 방식, 롤백 때 옛 컬럼을 삭제해도 되는지를 찾아 answer.json에 old_key,new_key,dual_days,index_method,drop_old_on_rollback 필드로 작성해. 마지막 값은 불리언이야. 원문에 근거한 답만 기록해."},
}


def document():
    sections = ["# Synthetic engineering handbook\n"]
    for i in range(320):
        sections.append(f"## Module {i:03d} operations\n\n"
            f"Module {i:03d} owns routine retry reporting, migration dashboards, and index metrics. "
            "Its background checks run every fifteen minutes. Review normal queue depth and "
            "deployment labels before opening a support ticket. These notes do not define "
            "Orchid API or Cedar consumer compatibility contracts. The module cache is optional. "
            "Owners retain diagnostic reports only during the synthetic exercise.\n")
    sections.insert(89, "## Orchid API retry contract\n\n"
        "Orchid retries only HTTP 429 and 503 when an idempotency key is present. "
        "The budget is four total attempts, including the first call. "
        "The attempt argument counts calls already completed. HTTP 400 validation failures "
        "must never be retried. Do not infer retry permission from the status-code family.\n")
    sections.insert(244, "## Cedar migration consumer contract\n\n"
        "Cedar keeps customer_id and adds account_ref. Return both keys for at least 30 days. "
        "Create the new lookup index concurrently. During rollback, keep the old column; "
        "do not drop customer_id. A deployment rollback is not permission to delete data.\n")
    sections.insert(180, "## Korean operations note\n\n"
        "한글 검색 확인: 결제 취소는 영수증 검증 후 처리한다. customer_id는 기존 응답 키다.\n")
    return "\n".join(sections)


def create(folder: Path):
    folder.mkdir(parents=True, exist_ok=False)
    (folder / "handbook.md").write_text(document(), encoding="utf-8")
    (folder / "app.py").write_text("def should_retry(status, attempt, keyed):\n    return status >= 400 and attempt <= 4\n", encoding="utf-8")


def acceptance(case, folder):
    import json
    import subprocess
    import sys
    if case == "migration":
        value = json.loads((folder / "answer.json").read_text(encoding="utf-8-sig"))
        return (value.get("old_key") == "customer_id" and value.get("new_key") == "account_ref"
                and value.get("dual_days") == 30 and value.get("index_method") == "concurrently"
                and value.get("drop_old_on_rollback") is False)
    # Independent boundaries; the model never receives this evaluator.
    code = "from app import should_retry\nfor s in [200,400,408,429,500,503,504]:\n for a in [1,2,3,4,5]:\n  for k in [True,False]:\n   assert should_retry(s,a,k) == (s in (429,503) and a < 4 and k), (s,a,k)\n"
    return subprocess.run([sys.executable, "-B", "-c", code], cwd=folder, capture_output=True, timeout=20).returncode == 0
