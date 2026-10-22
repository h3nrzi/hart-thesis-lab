#!/usr/bin/env python3
"""بررسی ساختار تخت پرونده‌ها و ممنوعیت نتیجه بدون اظهار صریح مدرس."""
from pathlib import Path
import re
import sys
from datetime import datetime
from prepare_outcome import closure_evidence

ROOT = Path(__file__).resolve().parent.parent
REQUIRED = ("README.md", "CONTRIBUTING.md", "INDEX.md", "docs/workflow.md",
            "docs/statuses.md", "templates/case.md", "templates/original.md",
            "templates/update.md", "templates/review.md", "templates/outcome.md",
            "analyses/README.md")
STATUS = re.compile(r"(?m)^- \*\*وضعیت پرونده:\*\*\s*(.+?)\s*$")
OUTCOME_STATUS = re.compile(r"(?m)^- \*\*وضعیت ارزیابی:\*\*\s*(.+?)\s*$")
EVENT = re.compile(r"(update|review)-(\d{8}T\d{6}Z)\.md\Z")

def audit(root):
    root = Path(root)
    errors = [f"فایل ضروری نیست: {p}" for p in REQUIRED if not (root/p).is_file()]
    count = 0
    for folder in sorted((root/"analyses").iterdir()) if (root/"analyses").is_dir() else []:
        if not folder.is_dir():
            continue
        count += 1
        if not re.fullmatch(r"[A-Za-z0-9]{4,32}", folder.name):
            errors.append(f"شناسه پرونده نامعتبر: {folder.name}")
        files = list(folder.iterdir())
        if any(x.is_dir() for x in files):
            errors.append(f"پوشه داخلی غیرمجاز: {folder.name}")
        case = folder/"case.md"
        original = folder/"original.md"
        outcome = folder/"outcome.md"
        if not case.is_file():
            errors.append(f"case.md مفقود: {folder.name}")
            continue
        txt = case.read_text(encoding="utf-8")
        if f"**شناسه ایده:** {folder.name}" not in txt or "**نشانی منبع:**" not in txt:
            errors.append(f"شناسنامه ناقص: {folder.name}")
        status_m = STATUS.search(txt)
        status = status_m.group(1).strip() if status_m else ""
        if not status:
            errors.append(f"وضعیت پرونده مشخص نیست: {folder.name}")
        if status != "در انتظار متن اولیه" and not original.exists():
            errors.append(f"وضعیت پرونده نیازمند original.md است: {folder.name}")
        updates = []
        for file in files:
            if file.name in ("case.md", "original.md", "outcome.md"):
                continue
            m = EVENT.fullmatch(file.name)
            if not file.is_file() or not m:
                errors.append(f"فایل نامعتبر در پرونده {folder.name}: {file.name}")
                continue
            try:
                datetime.strptime(m.group(2), "%Y%m%dT%H%M%SZ")
            except ValueError:
                errors.append(f"تاریخ نامعتبر رویداد: {file.name}")
            if not original.is_file():
                errors.append(f"رویداد بدون تحلیل اولیه: {file.name}")
            content = file.read_text(encoding="utf-8")
            if f"**شناسه ایده:** {folder.name}" not in content:
                errors.append(f"شناسه در رویداد مفقود: {file.name}")
            if m.group(1) == "update":
                updates.append(file)
        qualified = [p for p in updates if closure_evidence(p)]
        if outcome.exists():
            if not original.is_file() or not qualified:
                errors.append(f"outcome.md بدون اعلام مستند نتیجه توسط مدرس: {folder.name}")
            o = outcome.read_text(encoding="utf-8")
            m = OUTCOME_STATUS.search(o)
            state = m.group(1).strip() if m else ""
            if state not in ("پیش‌نویس", "تکمیل‌شده"):
                errors.append(f"وضعیت ارزیابی نامعتبر: {folder.name}")
            if not any(p.name in o for p in qualified):
                errors.append(f"نام آپدیت واجد شرایط در outcome.md نیست: {folder.name}")
            if state == "تکمیل‌شده" and status != "بسته‌شده":
                errors.append(f"نتیجه تکمیل‌شده اما پرونده بسته نشده: {folder.name}")
            if status == "بسته‌شده" and state != "تکمیل‌شده":
                errors.append(f"پرونده بسته‌شده نتیجه تکمیل‌شده ندارد: {folder.name}")
        elif status in ("بسته‌شده", "در حال تدوین نتیجه"):
            errors.append(f"وضعیت پرونده بدون outcome.md معتبر نیست: {folder.name}")
    return errors, count

if __name__ == "__main__":
    errors, count = audit(ROOT)
    if errors:
        print("اعتبارسنجی ناموفق:")
        for error in errors:
            print(" -", error)
        sys.exit(1)
    print(f"اعتبارسنجی موفق؛ {count} پرونده واقعی.")
