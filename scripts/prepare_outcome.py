#!/usr/bin/env python3
"""آماده‌سازی نتیجه تنها با اظهار مستند مدرس و هماهنگ‌سازی وضعیت پرونده."""
import argparse
from pathlib import Path
import re
from case_transitions import plan_status, apply_status

ROOT=Path(__file__).resolve().parent.parent
EVENT_NAME=re.compile(r"update-\d{8}T\d{6}Z\.md\Z")
SOURCE=re.compile(r"(?m)^- \*\*نشانی منبع:\*\*\s*(https://(?:www\.)?tradingview\.com/\S+)\s*$")
WITNESS=re.compile(r"(?m)^- \*\*شاهد بررسی نتیجه:\*\*\s*(.+)\s*$")

def closure_evidence(update):
    content=Path(update).read_text(encoding="utf-8")
    if not re.search(r"(?m)^- \*\*بررسی صریح نتیجه توسط مدرس:\*\*\s*بله\s*$",content):
        return False
    if not SOURCE.search(content):
        return False
    m=WITNESS.search(content)
    return bool(m and m.group(1).strip() not in ("نامشخص","-","هیچ","[شاهد]") and not m.group(1).strip().startswith("["))

def prepare(root,idea,update_name):
    root=Path(root)
    if not re.fullmatch(r"[A-Za-z0-9]{4,32}",idea):
        raise ValueError("شناسه پرونده نامعتبر است")
    if not EVENT_NAME.fullmatch(update_name):
        raise ValueError("نام آپدیت باید update-YYYYMMDDTHHMMSSZ.md باشد")
    folder=root/"analyses"/idea
    if not (folder/"case.md").is_file() or not (folder/"original.md").is_file():
        raise ValueError("شناسنامه و تحلیل اولیه باید ثبت شده باشند")
    update=folder/update_name
    if not update.is_file() or not closure_evidence(update):
        raise ValueError("سند اعلام نتیجه مدرس با لینک و شاهد موجود نیست")
    outcome=folder/"outcome.md"
    if outcome.exists():
        raise FileExistsError("outcome.md موجود است و بازنویسی نمی‌شود")
    planned=plan_status(root,idea,
        ("در حال پیگیری","در انتظار اعلام نتیجه مدرس"),"در حال تدوین نتیجه")
    template=(root/"templates"/"outcome.md").read_text(encoding="utf-8")
    content=template.replace("[شناسه]",idea).replace("[فایل آپدیت]",update_name)
    with outcome.open("x",encoding="utf-8") as fh:fh.write(content)
    apply_status(planned)
    return outcome

if __name__=="__main__":
    p=argparse.ArgumentParser(description="پیش‌نویس نتیجه مشروط با تغییر وضعیت هماهنگ")
    p.add_argument("--id",required=True);p.add_argument("--update",required=True)
    p.add_argument("--root",type=Path,default=ROOT,help=argparse.SUPPRESS)
    args=p.parse_args()
    try:print("پیش‌نویس ساخته شد:",prepare(args.root,args.id,args.update))
    except (ValueError,FileExistsError,FileNotFoundError) as err:p.exit(1,f"خطا: {err}\n")
