#!/bin/sh
set -eu
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
for python_cmd in python3 python; do
    if command -v "$python_cmd" >/dev/null 2>&1 &&
       "$python_cmd" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)'; then
        exec "$python_cmd" "$script_dir/install.py" "$@"
    fi
done
echo 'Python 3.10 이상을 설치한 뒤 다시 실행해 줘.' >&2
exit 1
