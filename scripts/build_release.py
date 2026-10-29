"""커밋된 파일만 버전 ZIP과 SHA-256 목록으로 묶는다. 설치본·인증·백업은 포함하지 않는다."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import zipfile
from install import check_path, InstallError

ROOT=Path(__file__).absolute().parent.parent


def git(*args):
    return subprocess.check_output(["git",*args],cwd=ROOT)


def build(output, ref="HEAD", expected_tag=None):
    sha=git("rev-parse","--verify","--end-of-options",ref+"^{commit}").decode().strip()
    version=git("show",sha+":VERSION").decode().strip()
    if not re.fullmatch(r"\d+\.\d+\.\d+",version): raise ValueError("invalid VERSION")
    if expected_tag and expected_tag!="v"+version: raise ValueError("tag and VERSION disagree")
    output=output.expanduser().absolute(); check_path(output)
    output=output.resolve()
    if output==ROOT or ROOT in output.parents: raise ValueError("release output must be outside source checkout")
    output.mkdir(parents=True,exist_ok=True)
    archive=output/f"minwoo-codex-kit-{version}.zip"
    manifest=output/"release.json"; sums=output/"SHA256SUMS"
    for path in (archive,manifest,sums):
        check_path(path)
        if path.exists(): raise ValueError("output exists; choose a new output folder")
    raw=git("-c","core.autocrlf=false","-c","core.eol=lf","archive","--format=zip","--prefix=minwoo-codex-kit/",sha)
    import io
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        names=[n for n in z.namelist() if not n.endswith("/")]
        for name in names:
            path=PurePosixPath(name)
            if path.is_absolute() or ".." in path.parts or path.parts[0]!="minwoo-codex-kit":
                raise ValueError("unsafe archive path")
            if any(part in {".git",".minwoo-codex-kit","node_modules","__pycache__","work",".venv"} for part in path.parts):
                raise ValueError("private/generated artifact")
            if path.name in {"auth.json","config.toml",".env"} or path.suffix in {".pem",".key",".pfx",".p12",".pyc"}:
                raise ValueError("private/generated artifact")
        if z.testzip() is not None: raise ValueError("invalid ZIP")
    archive.write_bytes(raw)
    metadata={"version":version,"commit":sha,"files":len(names),
              "skills":sum(name.endswith("/SKILL.md") for name in names)}
    manifest.write_text(json.dumps(metadata,indent=2)+"\n",encoding="utf-8",newline="\n")
    sums.write_text("".join(hashlib.sha256(p.read_bytes()).hexdigest()+"  "+p.name+"\n" for p in (archive,manifest)),
                    encoding="utf-8",newline="\n")
    return metadata


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--ref",default="HEAD")
    parser.add_argument("--tag")
    args=parser.parse_args()
    try: print(json.dumps(build(args.output,args.ref,args.tag),indent=2))
    except (OSError,ValueError,InstallError,subprocess.SubprocessError) as exc:
        raise SystemExit("Release failed: "+str(exc))
