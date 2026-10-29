"""고정된 공개 Python 패키지를 OSV에 조회한다. 누락·오류는 성공으로 처리하지 않는다."""
import json
from pathlib import Path
import re
import urllib.request


def audit(requirements):
    queries=[]
    for line in requirements.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"): continue
        match=re.match(r"([A-Za-z0-9_.-]+)==([^\s;]+)",line)
        if not match: raise ValueError("unrecognized pinned requirement")
        queries.append({"package":{"name":match[1],"ecosystem":"PyPI"},"version":match[2]})
    if not queries: raise ValueError("no packages assessed")
    request=urllib.request.Request("https://api.osv.dev/v1/querybatch",data=json.dumps({"queries":queries}).encode(),
                                  headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(request,timeout=60) as response: result=json.load(response)
    rows=result.get("results")
    if not isinstance(rows,list) or len(rows)!=len(queries): raise ValueError("incomplete OSV response")
    if any(not isinstance(row,dict) or "error" in row or not isinstance(row.get("vulns",[]),list) for row in rows):
        raise ValueError("invalid OSV result row")
    findings=[{"package":q["package"]["name"],"version":q["version"],
               "advisories":[v["id"] for v in r.get("vulns",[])]} for q,r in zip(queries,rows)]
    return findings


if __name__=="__main__":
    try:
        findings=audit(Path(__file__).resolve().parents[1]/"tooling/requirements.txt")
        print(json.dumps(findings,indent=2))
        raise SystemExit(1 if any(x["advisories"] for x in findings) else 0)
    except (OSError,ValueError,KeyError) as exc:
        raise SystemExit("OSV audit incomplete: "+str(exc))
