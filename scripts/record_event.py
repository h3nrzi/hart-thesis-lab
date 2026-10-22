#!/usr/bin/env python3
"""ثبت رویداد تاریخ‌دار بدون شبکه، و با شناسه محتوا برای جلوگیری از تکرار."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlparse
from agent_status import stage_for

ROOT = Path(__file__).resolve().parent.parent

def valid_tradingview(url):
    p = urlparse(url)
    return p.scheme == "https" and p.netloc.lower() in ("www.tradingview.com", "tradingview.com") and p.path.startswith("/chart/")

def record(root, idea, kind, text_file, source_url=None, published=None, declares_outcome=False, witness=None):
    root = Path(root)
    if not re.fullmatch(r"[A-Za-z0-9]{4,32}", idea):
        raise ValueError("شناسه پرونده نامعتبر")
    if kind not in ("update", "review"):
        raise ValueError("نوع رویداد نامعتبر")
    body = Path(text_file).read_text(encoding="utf-8").strip()
    if not body:
        raise ValueError("متن خالی است")
    if kind == "update" and not valid_tradingview(source_url or ""):
        raise ValueError("آپدیت باید نشانی معتبر ایده در TradingView داشته باشد")
    if kind == "review" and declares_outcome:
        raise ValueError("نقد AI نمی‌تواند اظهار نهایی مدرس باشد")
    if declares_outcome and (not witness or len(witness.strip()) < 12 or witness.strip() == "نامشخص"):
        raise ValueError("اعلام نتیجه مدرس باید شاهد روشنِ ارائه‌شده توسط کاربر داشته باشد")
    if witness and ("\n" in witness or "\r" in witness):
        raise ValueError("شاهد باید یک خط باشد")
    folder = root / "analyses" / idea
    key = {
        "kind": kind, "body": body, "source": source_url or "",
        "published": published or "نامشخص", "declares_outcome": bool(declares_outcome),
    }
    digest = hashlib.sha256(json.dumps(key, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
    marker = f"<!-- event-sha256: {digest} -->"
    # قبل از بررسی مرحله، رویدادِ تکراری را به همان سند موجود ارجاع بده.
    for file in sorted(folder.glob(kind + "-*.md")):
        if marker in file.read_text(encoding="utf-8"):
            return file, False
    stage = stage_for(root, idea)
    if stage["stage"] not in ("TRACKING", "READY_FOR_OUTCOME"):
        raise ValueError(f"ثبت رویداد در مرحله {stage['stage']} مجاز نیست")
    now = datetime.now(timezone.utc)
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    path = folder / f"{kind}-{stamp}.md"
    if path.exists():
        raise FileExistsError("نام رویداد در این ثانیه موجود است؛ آن را بازنویسی نکن")
    user_time = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    quoted = "\n".join("> " + s for s in body.splitlines())
    if kind == "update":
        content = (
            f"# آپدیت مدرس — {idea}\n\n"
            f"- **شناسه ایده:** {idea}\n"
            "- **منشأ اطلاعات:** آپدیت مدرس، استخراج‌شده و ارسال‌شده توسط کاربر\n"
            f"- **زمان انتشار توسط مدرس:** {published or 'نامشخص'}\n"
            f"- **زمان ثبت در مخزن (UTC):** {user_time}\n"
            f"- **نشانی منبع:** {source_url}\n"
            f"- **بررسی صریح نتیجه توسط مدرس:** {'بله' if declares_outcome else 'خیر'}\n"
            f"- **شاهد بررسی نتیجه:** {witness or 'نامشخص'}\n\n"
            f"## گفته مدرس، طبق متن ارسالی کاربر\n\n{quoted}\n\n{marker}\n"
        )
    else:
        content = (
            f"# نقد مستقل AI — {idea}\n\n"
            f"- **شناسه ایده:** {idea}\n"
            "- **منشأ اطلاعات:** برداشت مستقل AI؛ نه گفته مدرس\n"
            f"- **زمان ثبت در مخزن (UTC):** {user_time}\n\n"
            f"## بررسی آموزشی\n\n{quoted}\n\n{marker}\n"
        )
    with path.open("x", encoding="utf-8") as f:
        f.write(content)
    return path, True

if __name__ == "__main__":
    p=argparse.ArgumentParser(description="ثبت آپدیت مدرس از پیام کاربر یا نقد AI")
    p.add_argument("--id", required=True)
    p.add_argument("--kind", required=True, choices=("update", "review"))
    p.add_argument("--text-file", required=True)
    p.add_argument("--source-url", help="برای آپدیت مدرس اجباری است")
    p.add_argument("--published", help="زمان انتشار مدرس، اگر در داده کاربر هست")
    p.add_argument("--declares-outcome", action="store_true", help="فقط وقتی مدرس واقعاً پایان سناریو را بررسی کرده")
    p.add_argument("--witness", help="شاهد ارائه‌شده توسط کاربر برای بررسی صریح نتیجه")
    p.add_argument("--root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    args=p.parse_args()
    try:
        path, created=record(args.root,args.id,args.kind,args.text_file,
            args.source_url,args.published,args.declares_outcome,args.witness)
        print(("ثبت شد: " if created else "رویداد تکراری؛ سند موجود: ") + str(path))
    except (ValueError, FileNotFoundError, FileExistsError) as err:
        p.exit(1,f"خطا: {err}\n")
