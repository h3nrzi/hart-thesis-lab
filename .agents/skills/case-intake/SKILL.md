---
name: case-intake
description: Create or resume a TradingView analysis case from a user-submitted link without extracting the source text. Use when a link arrives or a case must be located.
---

# دریافت لینک و شناسنامه
۱. `python3 scripts/agent_status.py` و در صورت شناسه `--id` اجرا کن؛ اگر پرونده موجود است تکراری نساز.
۲. **فقط URL ارسالی کاربر** به `scripts/create_case.py --url` داده شود؛ اگر بازار/تایم‌فریم در پیام نیست، خالی.
۳. تأیید کن فقط `case.md` و `INDEX.md` ساخته یا تغییر کرده‌اند.
۴. به کاربر بگو منتظر متن استخراج‌شده تحلیل اولیه است. متن TradingView را جستجو/خواندن/تحلیل نکن.
۵. تغییر را فقط طبق `docs/concurrency.md` در شاخه و PR پیگیری کن.
