#!/usr/bin/env python3
"""ثبت فقط متن اولیه‌ای که کاربر فرستاده؛ بدون دسترسی به TradingView."""
import argparse
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import re
from agent_status import stage_for

ROOT = Path(__file__).resolve().parent.parent

def fingerprint(text):
    return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()

def record(root, idea, text_file):
    root = Path(root)
    if not re.fullmatch(r"[A-Za-z0-9]{4,32}", idea):
        raise ValueError("شناسه پرونده نامعتبر است")
    source = Path(text_file).read_text(encoding="utf-8").strip()
    if not source:
        raise ValueError("متن اولیه کاربر خالی است")
    folder = root / "analyses" / idea
    target = folder / "original.md"
    marker = f"<!-- content-sha256: {fingerprint(source)} -->"
    if target.is_file():
        if marker in target.read_text(encoding="utf-8"):
            return target, False
        raise FileExistsError("نسخه اولیه موجود و متفاوت است؛ اجازه بازنویسی نداریم")
    state = stage_for(root, idea)
    if state["stage"] != "AWAITING_ORIGINAL":
        raise ValueError(f"مرحله پرونده مناسب ثبت اولیه نیست: {state['stage']}")
    case = folder / "case.md"
    casetext = case.read_text(encoding="utf-8")
    case_new = casetext.replace("**وضعیت پرونده:** در انتظار متن اولیه",
                                "**وضعیت پرونده:** در حال پیگیری")
    if case_new == casetext:
        raise ValueError("وضعیت اولیه در case.md یافت نشد")
    index = root / "INDEX.md"
    rows = index.read_text(encoding="utf-8").splitlines(keepends=True)
    index_changed = False
    for i, line in enumerate(rows):
        if f"](analyses/{idea}/case.md)" in line:
            pieces = line.split("|")
            if len(pieces) < 8 or pieces[5].strip() != "در انتظار متن اولیه":
                raise ValueError("INDEX.md با وضعیت پرونده سازگار نیست")
            pieces[5] = " در حال پیگیری "
            rows[i] = "|".join(pieces)
            index_changed = True
    if not index_changed:
        raise ValueError("سطر پرونده در INDEX.md وجود ندارد")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    url_line = next((s.strip() for s in casetext.splitlines() if "**نشانی منبع:**" in s), "")
    url = url_line.split("**نشانی منبع:**", 1)[-1].strip() or "نامشخص"
    quoted = "\n".join("> " + line for line in source.splitlines())
    content = (f"# تحلیل اولیه — {idea}\n\n"
        f"- **شناسه ایده:** {idea}\n- **نشانی منبع:** {url}\n"
        f"- **منشأ اطلاعات:** استخراج و ارسال توسط کاربر\n"
        f"- **زمان انتشار تحلیل:** نامشخص\n"
        f"- **زمان ثبت در مخزن (UTC):** {now}\n\n"
        f"## متن یا خلاصه دریافتی\n\n{quoted}\n\n"
        f"## کمبودهای اطلاعاتی\n\nمواردی که کاربر ارائه نکرده، نامشخص هستند.\n\n{marker}\n")
    # O_EXCL: فایل موجود در سشن دیگر هرگز بازنویسی نشود.
    with target.open("x", encoding="utf-8") as f:
        f.write(content)
    case.write_text(case_new, encoding="utf-8")
    index.write_text("".join(rows), encoding="utf-8")
    return target, True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ثبت متن اولیه استخراج‌شده توسط کاربر")
    parser.add_argument("--id", required=True)
    parser.add_argument("--text-file", required=True, help="فایلی که کاربر متن را در آن قرار داده")
    parser.add_argument("--root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    args = parser.parse_args()
    try:
        filename, created = record(args.root, args.id, args.text_file)
        print(("ثبت شد: " if created else "قبلاً عیناً ثبت شده: ") + str(filename))
    except (ValueError, FileNotFoundError, FileExistsError) as err:
        parser.exit(1, f"خطا: {err}\n")
