# آزمایشگاه رهگیری تحلیل‌ها

متن مستندات فارسی و نام پوشه‌ها و فایل‌ها انگلیسی است. **هنوز هیچ پرونده واقعی ثبت نشده است.**

## ترتیب همکاری

۱. **پیام اول: فقط لینک.** فقط `analyses/<idea-id>/case.md` و ردیف `INDEX.md` ساخته می‌شوند. شناسه و نشانه نماد از خود نشانی قابل برداشت‌اند؛ بازار، تایم‌فریم و تحلیلگر اگر کاربر نداده باشد «نامشخص» می‌مانند. هیچ محتوایی از صفحه تریدینگ‌ویو استخراج نمی‌شود.

۲. **پیام دوم: استخراج کاربر.** تنها پس از ارسال متن یا خلاصه تحلیل اولیه توسط کاربر، `original.md` نوشته می‌شود.

۳. **پیام‌های بعدی: آپدیت مدرس توسط کاربر.** هر آپدیت در فایل `update-YYYYMMDDTHHMMSSZ.md` و هر نقد AI در فایل `review-YYYYMMDDTHHMMSSZ.md`، همگی **مستقیماً داخل پوشه همان پرونده** قرار می‌گیرند.

۴. **نتیجه نهایی مشروط.** `outcome.md` فقط بعد از آپدیت مستند مدرس که **صریحاً نتیجه یا پایان سناریو را بررسی کرده** و کاربر آن را فرستاده، به‌صورت پیش‌نویس ایجاد می‌شود. بسته‌شدن پرونده نیازمند تکمیل همان نتیجه است؛ نظر AI یا حرکت قیمت به‌تنهایی مجوز نیست.

```text
analyses/<idea-id>/
  case.md
  original.md
  update-YYYYMMDDTHHMMSSZ.md
  review-YYYYMMDDTHHMMSSZ.md
  outcome.md
```

در لحظه ارسال لینک **فقط case.md** وجود دارد؛ سایر نام‌ها نمای ساختارِ مراحل بعدی هستند.

## ورود ایجنت‌ها\n\nبرای Codex و Antigravity، [راهنمای راه‌اندازی](docs/agent-onboarding.md)، [قرارداد مشترک AGENTS.md](AGENTS.md) و [ماشین حالت](docs/state-machine.md) مبنا هستند. بدون نیاز به حافظه چت، `python3 scripts/agent_status.py` مرحله و سؤال بعدی را مشخص می‌کند. مهارت‌های بازار در `.agents/skills/` و دستورالعمل هم‌زمانی در `docs/concurrency.md` قرار دارند.\n\nبرای جلوگیری از توقف بی‌مورد با فایل‌های کش پایتون، `.gitignore` و `scripts/check_worktree.py` معیار بررسی تغییرات محلی‌اند؛ ایجنت هیچ فایلی را برای پاک‌سازی محیط حذف نمی‌کند.

## اسناد

[چرخه کار](docs/workflow.md) · [قواعد ثبت شواهد](CONTRIBUTING.md) · [وضعیت‌ها](docs/statuses.md) · [معیارهای ارزیابی](docs/evaluation-criteria.md) · [فهرست پرونده‌ها](INDEX.md) · [قالب‌ها](templates/README.md)

ابزارها: `scripts/create_case.py`، `scripts/record_original.py`، `scripts/record_event.py`، `scripts/agent_status.py`، `scripts/prepare_outcome.py`، `scripts/finalize_outcome.py` و `scripts/validate_structure.py`. هیچ استخراج خودکار یا پایش بازار در مخزن فعال نیست. این پروژه صرفاً آموزشی است و سوددهی هیچ معامله‌گری را تأیید نمی‌کند.
