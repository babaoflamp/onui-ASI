#!/bin/bash
# onui-ai 서비스 재시작

PORT=9002
DIR="$(cd "$(dirname "$0")" && pwd)"

# 기존 프로세스 종료
PID=$(lsof -ti :$PORT)
if [ -n "$PID" ]; then
    echo "기존 프로세스 종료 (PID: $PID)..."
    kill -9 $PID
    sleep 1
fi

# 재시작
echo "포트 $PORT 에서 서버 시작..."
nohup "$DIR/.venv/bin/python3" -m uvicorn main:app \
    --host 0.0.0.0 --port $PORT --reload \
    > "$DIR/logs/uvicorn.log" 2>&1 &

echo "PID: $!"
sleep 3
tail -4 "$DIR/logs/uvicorn.log"
