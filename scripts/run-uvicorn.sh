#!/bin/bash
cd /home/scottk/Projects/onui-ASI
source .venv/bin/activate

export ONUI_TMP_DIR="${ONUI_TMP_DIR:-/home/scottk/Projects/onui-ASI/data/tmp}"
export TMPDIR="${TMPDIR:-$ONUI_TMP_DIR}"
export TEMP="${TEMP:-$ONUI_TMP_DIR}"
export TMP="${TMP:-$ONUI_TMP_DIR}"
mkdir -p "$ONUI_TMP_DIR"

exec python -m uvicorn main:app --host 0.0.0.0 --port 9002
