#!/usr/bin/env python3
"""کنترل تغییرات تاریخی با مقایسه دو commit؛ روی PR و push اجرا می‌شود."""
import argparse
import re
import subprocess
from pathlib import PurePosixPath

IMMUTABLE = re.compile(r"^analyses/[^/]+/(original|(?:update|review)-\d{8}T\d{6}Z)\.md$")
DURABLE = re.compile(r"^analyses/[^/]+/(case|outcome)\.md$")

def changed(base, head="HEAD", cwd=None):
    proc = subprocess.run(["git", "diff", "--name-status", "--no-renames", base, head],
        cwd=cwd, capture_output=True, text=True, check=True)
    return [(line.split("\t",1)[0], line.split("\t",1)[1]) for line in proc.stdout.splitlines() if "\t" in line]

def policy(base, head="HEAD", cwd=None):
    errors = []
    changes = changed(base, head, cwd)
    for state, path in changes:
        if IMMUTABLE.fullmatch(path) and state != "A":
            errors.append(f"سند اولیه/رویداد تاریخ‌دار نباید حذف یا بازنویسی شود: {state} {path}")
        if DURABLE.fullmatch(path) and state == "D":
            errors.append(f"حذف شناسنامه/نتیجه پرونده ممنوع است: {path}")
        if path.startswith("analyses/") and path.count("/") > 2:
            errors.append(f"سند پرونده نباید در زیرپوشه قرار بگیرد: {path}")
    return errors

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="بررسی سیاست منع بازنویسی سابقه تحلیل‌ها")
    parser.add_argument("--base", required=True, help="SHA پایه واقعی PR یا push")
    parser.add_argument("--head", default="HEAD")
    args = parser.parse_args()
    try:
        issues = policy(args.base, args.head)
    except (subprocess.SubprocessError, OSError) as err:
        parser.exit(2, f"خطا در Git: {err}\n")
    for issue in issues:
        print("رد شد:", issue)
    if issues:
        raise SystemExit(1)
    print("سیاست تغییرات تاریخی رعایت شده است.")
