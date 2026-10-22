# قرارداد اجرایی ایجنت‌های مستقل از سشن

## منبع حقیقت
۱. Git branch/commit واقعی؛ ۲. اسناد `analyses/<id>/`؛ ۳. خروجی `scripts/agent_status.py`؛ ۴. توضیح گفتگو فقط **ورودی کاربر** است، نه وضعیت سابق.
`INDEX.md` برای مشاهده سریع است، نه مرجع تصمیم. در صورت اختلاف با پرونده، ابتدا توقف و اصلاح مستند.

## راه‌اندازی قابل تکرار در Codex/Antigravity
```bash
git status --short
git rev-parse HEAD
python3 -B scripts/check_worktree.py
python3 -B scripts/agent_status.py
python3 -B scripts/validate_structure.py
```
اگر `--id` داده شد، وضعیت همان پرونده را بخوان. پوشه‌های ignored مانند `__pycache__` نباید حذف شوند یا جلوی عملیات را بگیرند؛ فقط خروجی `check_worktree.py` با `clean: false` مانع تغییر است. خروجی `agent_status` شامل `stage`، `next_question`، `allowed_actions` و `blockers` است. ابتدا ابزار را اجرا، سپس مطابق وضعیت عمل کن. اگر مرحله `CONFLICT` بود، دست نزن.

## فرمان‌های کار با پرونده
- لینک: `python3 scripts/create_case.py --url "<link>"`؛ فقط case و INDEX ایجاد می‌شوند.
- متن اولیه: کاربر متن را در فایل ورودی محلی می‌دهد؛ `python3 scripts/record_original.py --id <id> --text-file <user-text.txt>` نسخه اولیه را بدون دانلود از TradingView ثبت کرده و case/INDEX را هماهنگ می‌کند. اجرای مجدد متن یکسان بدون اثر است.
- آپدیت مدرس: `python3 scripts/record_event.py --id <id> --kind update --text-file <user-update.txt> --source-url <url>`؛ اگر مدرس نتیجه را صریحاً بررسی کرده، فقط با شواهد ارسالی کاربر `--declares-outcome --witness <evidence>` مجاز است. سند تکراری ایجاد نمی‌شود.
- نقد AI: `python3 scripts/record_event.py --id <id> --kind review --text-file <ai-review.txt>` و ثبت مستقل در همان پوشه. تکرار متن یکسان سند دوباره نمی‌سازد.
- نتیجه: تنها بعد از اعلام صریح مدرس، `python3 scripts/prepare_outcome.py --id <id> --update <file>` پیش‌نویس می‌دهد؛ سپس بعد از تکمیل شواهد و جای‌نگهدارها، `python3 scripts/finalize_outcome.py --id <id>` پرونده را با کنترل و هماهنگی INDEX می‌بندد.

## پروتکل سؤال (حداقل سؤال لازم)
| حالت | سؤال فقط در نبود اطلاعات |
|---|---|
| `AWAITING_LINK` | «لینک تحلیل TradingView را می‌فرستی؟» |
| `AWAITING_ORIGINAL` | «متن یا خلاصه تحلیل اولیه‌ای که استخراج کردی را بفرست.» |
| `TRACKING` | «آپدیت جدید مدرس را می‌فرستی یا می‌خواهی همین اسناد را نقد کنیم؟» |
| `READY_FOR_OUTCOME` | «طبق آپدیت نتیجه‌ای که فرستادی، پیش‌نویس نتیجه را ثبت کنم؟» (اگر دستور ثبت داده، مستقیم عمل کن) |
| `DRAFT_OUTCOME` | «برای تکمیل نهایی، آیا نکته یا سند دیگری از اظهار مدرس باقی مانده؟» (اگر کافی است، تکمیل کن) |
| `CLOSED` | «پرونده بسته شده؛ پرونده جدید یا مرور آموزشی؟» |
| `CONFLICT` | «در مخزن ناسازگاری هست؛ ابتدا اجازه اصلاح این تعارض مشخص را می‌دهی؟» |

## خروجی ثابت هر نوبت
`شناسه | مرحله | اتفاق ثبت‌شده یا عدم تغییر | مدارک/فایل‌ها | وضعیت اعتبارسنجی | سؤال/عمل بعدی`.

**هرگز** نقش استخراج متن یا به‌روزرسانی‌ها را از کاربر نگیری؛ حتی اگر مرورگر در دسترس باشد. سشن جدید نباید بر اساس حافظه قبلی مرحله را حدس بزند.
