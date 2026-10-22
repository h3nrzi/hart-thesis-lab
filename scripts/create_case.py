#!/usr/bin/env python3
"""ساخت پرونده خام فقط از URL و فراداده صریح کاربر؛ بدون دریافت شبکه یا تحلیل."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import re
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
MARKER = "<!-- ردیف‌های تازه باید پیش از این خط افزوده شوند. -->"

def safe_text(value):
    value = (value or "نامشخص").strip()
    if not value or "\n" in value or "\r" in value or "|" in value:
        raise ValueError("مقدار ورودی نباید خالی، چندخطی یا دارای علامت | باشد.")
    return value

def parse_url(url):
    p = urlparse(url)
    if p.scheme != "https" or p.netloc.lower() not in ("www.tradingview.com", "tradingview.com"):
        raise ValueError("لینک باید HTTPS و متعلق به تریدینگ‌ویو باشد.")
    seg = [x for x in p.path.split("/") if x]
    if len(seg) < 3 or seg[0] != "chart":
        raise ValueError("فرمت مورد انتظار: /chart/<symbol>/<idea-id>-title/")
    idea = seg[2].split("-", 1)[0]
    if not re.fullmatch(r"[A-Za-z0-9]{4,32}", idea):
        raise ValueError("شناسه ایده قابل تشخیص نیست.")
    symbol = seg[1] if re.fullmatch(r"[A-Za-z0-9._:]{2,40}", seg[1]) else "نامشخص"
    return idea, symbol

def create_case(root, url, market=None, timeframe=None, analyst=None):
    idea, symbol = parse_url(url)
    root = Path(root)
    folder = root / "analyses" / idea
    index = root / "INDEX.md"
    index_text = index.read_text(encoding="utf-8")
    if MARKER not in index_text:
        raise ValueError("نشانگر افزودن پرونده در INDEX.md یافت نشد.")
    if folder.exists():
        raise FileExistsError("پرونده از قبل وجود دارد؛ هیچ داده‌ای بازنویسی نشد.")
    market, timeframe, analyst = map(safe_text, (market, timeframe, analyst))
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    case = (root / "templates" / "case.md").read_text(encoding="utf-8")
    for key, val in {"[شناسه]":idea, "[نشانی]":url, "[نماد]":symbol,
                     "[بازار]":market, "[تایم‌فریم]":timeframe,
                     "[تحلیلگر]":analyst, "[زمان ساخت]":timestamp}.items():
        case = case.replace(key, val)
    folder.mkdir(parents=True)
    (folder / "case.md").write_text(case, encoding="utf-8")
    row = f"| [{idea}](analyses/{idea}/case.md) | {symbol} | {market} | {timeframe} | در انتظار متن اولیه | [منبع]({url}) |"
    index.write_text(index_text.replace(MARKER, row + "\n\n" + MARKER), encoding="utf-8")
    return folder

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="فقط ساخت پرونده خام از لینک")
    parser.add_argument("--url", required=True)
    parser.add_argument("--market")
    parser.add_argument("--timeframe")
    parser.add_argument("--analyst")
    parser.add_argument("--root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    args = parser.parse_args()
    try:
        print("پرونده خام ساخته شد:", create_case(args.root, args.url, args.market, args.timeframe, args.analyst))
        print("منتظر متن تحلیل اولیه از طرف کاربر؛ original.md ساخته نشد.")
    except (ValueError, FileNotFoundError, FileExistsError) as exc:
        parser.exit(1, f"خطا: {exc}\n")
