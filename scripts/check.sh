#!/bin/sh
# Run from any directory; SALAM and PYTHON may point to specific executables.
set -eu
project_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$project_root"
salam=${SALAM:-salam}
python=${PYTHON:-python3}
mkdir -p build/linux
"$salam" build src/main.salam --target=x86_64-linux-musl --output=build/linux/subtitle-check --log-level=error
"$salam" build tests/unit.salam --target=x86_64-linux-musl --output=build/linux/unit --log-level=error
./build/linux/unit
"$python" tests/e2e.py build/linux/subtitle-check
