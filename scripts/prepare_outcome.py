#!/usr/bin/env python3
"""فقط با آپدیت مستندِ اعلام صریح نتیجه توسط مدرس، پیش‌نویس outcome.md ایجاد کن."""
import argparse
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
EVENT_NAME = re.compile(r"update-\d{8}T\d{6}Z\.md\Z")
SOURCE = re.compile(r"(?m)^- \*\*نشانی منبع:\*\*\s*(https://(?:www\.)?tradingview\.com/\S+)\s*$")
WITNESS = re.compile(r"(?m)^- \*\*شاهد بررسی نتیجه:\*\*\s*(.+)\s*$")

def closure_evidence(update):
    content = Path(update).read_text(encoding="utf-8")
    if not re.search(r"(?m)^- \*\*بررسی صریح نتیجه توسط مدرس:\*\*\s*بله\s*$", content):
        return False
    if not SOURCE.search(content):
        return False
    m = WITNESS.search(content)
    return bool(m and m.group(1).strip() not in ("نامشخص", "-", "هیچ", "[شاهد]") and not m.group(1).strip().startswith("["))

def prepare(root, idea, update_name):
    if not re.fullmatch(r"[A-Za-z0-9]{4,32}", idea):
        raise ValueError("شناسه پرونده نامعتبر است.")
    if not EVENT_NAME.fullmatch(update_name):
        raise ValueError("نام آپدیت باید update-YYYYMMDDTHHMMSSZ.md باشد.")
    folder = Path(root) / "analyses" / idea
    if not (folder / "case.md").is_file() or not (folder / "original.md").is_file():
        raise ValueError("شناسنامه و تحلیل اولیه ارسالی کاربر باید وجود داشته باشند.")
    update = folder / update_name
    if not update.is_file() or not closure_evidence(update):
        raise ValueError("آپدیت صریح مدرس با لینک منبع و شاهد معتبر موجود نیست.")
    dest = folder / "outcome.md"
    if dest.exists():
        raise FileExistsError("outcome.md موجود است و نباید بازنویسی شود.")
    template = (Path(root) / "templates" / "outcome.md").read_text(encoding="utf-8")
    template = template.replace("[شناسه]", idea).replace("[فایل آپدیت]", update_name)
    dest.write_text(template, encoding="utf-8")
    return dest

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="آماده‌سازی مشروط پیش‌نویس ارزیابی")
    parser.add_argument("--id", required=True)
    parser.add_argument("--update", required=True)
    parser.add_argument("--root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    args = parser.parse_args()
    try:
        print("پیش‌نویس نتیجه ایجاد شد، نه خاتمه نهایی:", prepare(args.root, args.id, args.update))
    except (ValueError, FileExistsError, FileNotFoundError) as exc:
        parser.exit(1, f"خطا: {exc}\n")
