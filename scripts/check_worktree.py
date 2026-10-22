#!/usr/bin/env python3
"""بررسی فقط‌خواندنی Git: فایل‌های ignored مانع کار نیستند، تغییر واقعی مانع است."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent


def inspect(root):
    cmd = ["git", "-C", str(Path(root)), "status", "--porcelain=v1", "--untracked-files=all"]
    result = subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=10)
    changes = [line for line in result.stdout.splitlines() if line]
    # Git status فایل‌های مطابق .gitignore را به صورت پیش‌فرض نشان نمی‌دهد.
    return {"clean": not changes, "changes": changes,
            "next_action": ("proceed" if not changes else "stop_and_report"),
            "ignored_files_are_not_blockers": True}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="کنترل تمیزی Git بدون حذف هیچ فایل")
    parser.add_argument("--root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    args = parser.parse_args()
    try:
        state = inspect(args.root)
    except (OSError, subprocess.SubprocessError) as exc:
        parser.exit(2, f"خطا در خواندن Git: {exc}\n")
    print(json.dumps(state, ensure_ascii=False, indent=2))
    if not state["clean"]:
        sys.exit(1)
