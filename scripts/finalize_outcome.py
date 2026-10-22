#!/usr/bin/env python3
"""نهایی‌سازی پیش‌نویس تکمیل‌شده و هماهنگ‌سازی case/INDEX بدون استخراج بازار."""
import argparse
from pathlib import Path
import re
from case_transitions import plan_status, apply_status
from prepare_outcome import closure_evidence

ROOT=Path(__file__).resolve().parent.parent
REF=re.compile(r"(?m)^- \*\*آپدیت مستند بررسی نتیجه توسط مدرس:\*\*\s*(update-\d{8}T\d{6}Z\.md)\s*$")

def finalize(root,idea):
    root=Path(root)
    if not re.fullmatch(r"[A-Za-z0-9]{4,32}",idea):
        raise ValueError("شناسه نامعتبر است")
    folder=root/"analyses"/idea
    path=folder/"outcome.md"
    if not path.is_file() or not (folder/"original.md").is_file():
        raise ValueError("برای نهایی‌سازی به تحلیل اولیه و پیش‌نویس نتیجه نیاز است")
    content=path.read_text(encoding="utf-8")
    if "- **وضعیت ارزیابی:** پیش‌نویس" not in content:
        raise ValueError("نتیجه در وضعیت پیش‌نویس نیست")
    ref=REF.search(content)
    if not ref or not (folder/ref.group(1)).is_file() or not closure_evidence(folder/ref.group(1)):
        raise ValueError("ارجاع معتبر به سند اعلام نتیجه مدرس وجود ندارد")
    if re.search(r"\[[^\[\]\n]{4,}\]",content):
        raise ValueError("جای‌نگهدارهای قالب هنوز تکمیل نشده‌اند؛ نتیجه را بررسی و پر کن")
    planned=plan_status(root,idea,("در حال تدوین نتیجه",),"بسته‌شده")
    path.write_text(content.replace("- **وضعیت ارزیابی:** پیش‌نویس",
                                   "- **وضعیت ارزیابی:** تکمیل‌شده"),encoding="utf-8")
    apply_status(planned)
    return path

if __name__=="__main__":
    p=argparse.ArgumentParser(description="نهایی کردن نتیجه فقط با متن و مدرک کامل")
    p.add_argument("--id",required=True);p.add_argument("--root",type=Path,default=ROOT,help=argparse.SUPPRESS)
    args=p.parse_args()
    try:print("پرونده بسته شد:",finalize(args.root,args.id))
    except (ValueError,FileNotFoundError) as err:p.exit(1,f"خطا: {err}\n")
