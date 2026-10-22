#!/usr/bin/env python3
# با اجرای دستی و یک پیوند معتبر، پوشه‌های خالی و قالب تحلیل اولیه می‌سازد.
# این ابزار متن منبع یا قیمت را استخراج نمی‌کند و تحلیلی انجام نمی‌دهد.
import argparse
from pathlib import Path
import re
import sys
from urllib.parse import urlparse

ریشه = Path(__file__).resolve().parent.parent
فرمان = argparse.ArgumentParser(description="ایجاد پرونده خام از نشانی تریدینگ‌ویو")
فرمان.add_argument("--url", required=True, help="نشانی مستقیم ایده در تریدینگ‌ویو")
ورودی = فرمان.parse_args()
نشانی = ورودی.url.strip()
نشانی_تجزیه = urlparse(نشانی)

if نشانی_تجزیه.scheme != "https" or نشانی_تجزیه.netloc.lower() not in ("tradingview.com", "www.tradingview.com"):
    sys.exit("خطا: نشانی باید متعلق به تریدینگ‌ویو و دارای HTTPS باشد.")
اجزا = [بخش for بخش in نشانی_تجزیه.path.split("/") if بخش]
if len(اجزا) < 3 or اجزا[0] != "chart" or not re.fullmatch(r"[A-Za-z0-9]+", اجزا[2].split("-", 1)[0]):
    sys.exit("خطا: شناسه ایده از نشانی قابل تشخیص نیست.")
شناسه = اجزا[2].split("-", 1)[0]
مسیر = ریشه / "analyses" / شناسه
if مسیر.exists():
    sys.exit("پرونده‌ای با همین شناسه موجود است؛ چیزی بازنویسی نشد.")

الگو = (ریشه / "templates" / "original.md").read_text(encoding="utf-8")
الگو = الگو.replace("[شناسه]", شناسه).replace("[نشانی]", نشانی)
مسیر.mkdir(parents=True)
(مسیر / "original.md").write_text(الگو, encoding="utf-8")
for نوع in ("updates", "reviews", "evaluations"):
    (مسیر / نوع).mkdir()
    (مسیر / نوع / ".gitkeep").write_text("", encoding="utf-8")

فهرست = ریشه / "INDEX.md"
متن = فهرست.read_text(encoding="utf-8")
نشانگر = "<!-- ردیف‌های تازه باید پیش از این خط افزوده شوند. -->"
if نشانگر not in متن:
    sys.exit("پرونده ساخته شد، اما نشانگر فهرست یافت نشد؛ فهرست را دستی بررسی کنید.")
سطر = f"| [{شناسه}](analyses/{شناسه}/original.md) | نامشخص | نامشخص | در انتظار تکمیل | نامشخص | ندارد | [منبع]({نشانی}) |\n"
متن = متن.replace(نشانگر, سطر + "\n" + نشانگر)
متن = متن.replace("**هنوز هیچ تحلیلی ثبت نشده است.**", "پرونده‌های ایجادشده در این فهرست ثبت می‌شوند؛ تکمیل شواهد هر پرونده جداگانه انجام می‌شود.")
فهرست.write_text(متن, encoding="utf-8")
print(f"پرونده خام «{شناسه}» ساخته شد؛ هنوز هیچ تحلیل یا نتیجه‌ای تأیید نشده است.")
