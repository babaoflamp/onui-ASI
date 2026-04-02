#!/usr/bin/env python3
"""
onui-ai 로그 로테이션 스크립트
실행: daily (cron으로 등록)
- pm2-error.log, pm2-out.log, detailed.log 대상
- 10 MB 초과 또는 날짜 변경 시 로테이션
- 최대 14개 백업 보관 (2주치)
"""

import os
import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path

LOG_DIR     = Path("/home/scottk/Projects/onui-ai/logs")
TARGETS     = ["pm2-error.log", "pm2-out.log", "detailed.log"]
MAX_SIZE_MB = 10          # 이 크기 넘으면 즉시 로테이션
KEEP_DAYS   = 14          # 보관 기간 (일)
NOW         = datetime.now()
DATE_STR    = NOW.strftime("%Y-%m-%d")

def rotate_log(log_path: Path):
    """로그 파일을 날짜-순번 이름으로 압축 백업"""
    if not log_path.exists() or log_path.stat().st_size == 0:
        print(f"  [SKIP] {log_path.name} (없음 or 빈 파일)")
        return

    size_mb = log_path.stat().st_size / 1024 / 1024
    print(f"  [INFO] {log_path.name}  {size_mb:.1f} MB")

    # 이름 충돌 방지: 같은 날짜 백업이 있으면 순번 증가
    for seq in range(1, 100):
        suffix = f".{DATE_STR}.{seq:02d}.gz"
        backup_path = log_path.with_suffix(suffix)
        if not backup_path.exists():
            break

    # 현재 로그를 gzip 압축 백업
    with open(log_path, "rb") as f_in:
        with gzip.open(backup_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

    # 원본 비우기 (프로세스가 파일을 열고 있어도 안전)
    with open(log_path, "w") as f:
        f.truncate(0)

    print(f"  [OK]   → {backup_path.name}  ({size_mb:.1f} MB)")


def cleanup_old_logs():
    """KEEP_DAYS 이상 된 .gz 백업 파일 삭제"""
    cutoff = NOW - timedelta(days=KEEP_DAYS)
    removed = 0
    for gz_file in LOG_DIR.glob("*.gz"):
        if gz_file.stat().st_mtime < cutoff.timestamp():
            gz_file.unlink()
            print(f"  [DEL]  {gz_file.name}")
            removed += 1
    if removed == 0:
        print("  [OK]   오래된 백업 없음")


def main():
    print("=" * 55)
    print(f"  [로그 로테이션] {NOW.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 55)

    print("\n▶ 로그 로테이션")
    for target in TARGETS:
        log_path = LOG_DIR / target
        size_mb = log_path.stat().st_size / 1024 / 1024 if log_path.exists() else 0
        if size_mb >= MAX_SIZE_MB:
            rotate_log(log_path)
        else:
            print(f"  [SKIP] {target}  {size_mb:.1f} MB (< {MAX_SIZE_MB} MB)")

    print(f"\n▶ 오래된 백업 정리 (>{KEEP_DAYS}일)")
    cleanup_old_logs()

    print("\n[완료]")


if __name__ == "__main__":
    main()
