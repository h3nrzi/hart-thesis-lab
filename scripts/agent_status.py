#!/usr/bin/env python3
"""وضعیت مستقل از سشن: بدون شبکه و بدون تغییر فایل."""
import argparse
import json
import re
import subprocess
from pathlib import Path
from prepare_outcome import closure_evidence
from validate_structure import audit

ROOT = Path(__file__).resolve().parent.parent
STATUS_RE = re.compile(r"(?m)^- \*\*وضعیت پرونده:\*\*\s*(.+?)\s*$")
OUTCOME_RE = re.compile(r"(?m)^- \*\*وضعیت ارزیابی:\*\*\s*(.+?)\s*$")
VALID_ID = re.compile(r"[A-Za-z0-9]{4,32}\Z")
UPDATE_NAME = re.compile(r"update-\d{8}T\d{6}Z\.md\Z")

NEXT = {
    "AWAITING_LINK": ("لینک تحلیل TradingView را می‌فرستی؟", ["create_case"], "هنوز شناسه پرونده مشخص نیست"),
    "AWAITING_ORIGINAL": ("متن یا خلاصه تحلیل اولیه‌ای که استخراج کردی را بفرست.", ["record_original"], "فقط شناسنامه اولیه داریم"),
    "TRACKING": ("آپدیت جدید مدرس را می‌فرستی یا می‌خواهی همین اسناد را نقد کنیم؟", ["record_update", "record_review"], "پرونده در حال پیگیری است"),
    "READY_FOR_OUTCOME": ("طبق آپدیت مستند نتیجه که فرستادی، پیش‌نویس نتیجه را ثبت کنم؟", ["prepare_outcome", "record_review"], "مدرک نتیجه مدرس موجود است"),
    "DRAFT_OUTCOME": ("آیا مستند دیگری برای تکمیل نهایی نتیجه لازم است؟", ["complete_outcome"], "نتیجه فقط در حد پیش‌نویس است"),
    "CLOSED": ("این پرونده بسته است؛ مرور آموزشی یا پرونده جدید؟", ["read_only"], "پرونده تکمیل شده است"),
    "CONFLICT": ("در پرونده ناسازگاری وجود دارد؛ ابتدا تعارض گزارش‌شده را رفع کنیم؟", ["stop_and_resolve"], "مرحله نامعتبر است"),
    "NOT_FOUND": ("پرونده پیدا نشد؛ لینک اصلی تحلیل را می‌فرستی؟", ["create_case"], "شناسه در مخزن ثبت نشده است"),
}

def head_sha(root):
    try:
        proc = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=True, timeout=3)
        return proc.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None

def stage_for(root, idea):
    root = Path(root)
    case_dir = root / "analyses" / idea
    if not case_dir.is_dir():
        return {"id": idea, "stage": "NOT_FOUND", "blockers": []}
    case = case_dir / "case.md"
    if not case.exists():
        return {"id": idea, "stage": "CONFLICT", "blockers": ["case.md مفقود است"]}
    content = case.read_text(encoding="utf-8")
    m = STATUS_RE.search(content)
    declared = m.group(1).strip() if m else None
    original = (case_dir / "original.md").is_file()
    updates = sorted(case_dir.glob("update-*.md"))
    qualified = [p.name for p in updates if UPDATE_NAME.fullmatch(p.name) and closure_evidence(p)]
    outcome_file = case_dir / "outcome.md"
    outcome = outcome_file.is_file()
    result_status = None
    if outcome:
        text = outcome_file.read_text(encoding="utf-8")
        m = OUTCOME_RE.search(text)
        result_status = m.group(1).strip() if m else None
    if not original:
        stage = "AWAITING_ORIGINAL"
        allowed_status = ("در انتظار متن اولیه",)
    elif not outcome:
        stage = "READY_FOR_OUTCOME" if qualified else "TRACKING"
        allowed_status = ("در حال پیگیری", "در انتظار اعلام نتیجه مدرس")
    elif result_status == "پیش‌نویس":
        stage = "DRAFT_OUTCOME"
        allowed_status = ("در حال تدوین نتیجه",)
    elif result_status == "تکمیل‌شده":
        stage = "CLOSED"
        allowed_status = ("بسته‌شده",)
    else:
        stage = "CONFLICT"
        allowed_status = tuple()
    blockers = []
    if declared not in allowed_status:
        blockers.append(f"وضعیت case.md با فایل‌های موجود سازگار نیست: {declared!r}؛ انتظار یکی از {allowed_status}")
    if not original and (updates or outcome):
        blockers.append("آپدیت یا نتیجه پیش از متن اولیه ثبت شده است")
    if outcome and not qualified:
        blockers.append("outcome.md فاقد سند اعلام صریح نتیجه توسط مدرس است")
    if outcome and qualified and not any(n in outcome_file.read_text(encoding="utf-8") for n in qualified):
        blockers.append("نتیجه به آپدیت واجد شرایط ارجاع نمی‌دهد")
    if any(x.is_dir() for x in case_dir.iterdir()):
        blockers.append("زیرپوشه در پرونده وجود دارد؛ ساختار باید تخت باشد")
    if blockers:
        stage = "CONFLICT"
    return {"id": idea, "stage": stage, "declared_status": declared, "has_original": original,
            "update_count": len(updates), "qualified_outcome_updates": qualified,
            "has_outcome": outcome, "blockers": blockers}

def inspect(root, idea=None):
    root = Path(root)
    errors, count = audit(root)
    head = head_sha(root)
    if idea:
        if not VALID_ID.fullmatch(idea):
            stage = {"id": idea, "stage": "CONFLICT", "blockers": ["شناسه نامعتبر است"]}
        else:
            stage = stage_for(root, idea)
        # A conflict in any other case should also prevent blind repository writes.
        if errors and stage["stage"] != "CONFLICT":
            stage["blockers"] += ["خطای اعتبارسنجی در مخزن: " + e for e in errors]
            stage["stage"] = "CONFLICT"
    else:
        ids = sorted(p.name for p in (root / "analyses").iterdir() if p.is_dir()) if (root / "analyses").exists() else []
        stage = {"id": None, "stage": "CONFLICT" if errors else "AWAITING_LINK",
                 "blockers": errors, "cases": [stage_for(root, i) for i in ids]}
        if any(c["stage"] == "CONFLICT" for c in stage["cases"]):
            stage["stage"] = "CONFLICT"
            stage["blockers"].append("حداقل یک پرونده ناسازگار است")
    prompt, actions, explanation = NEXT[stage["stage"]]
    return {**stage, "repository_head": head, "total_cases": count,
            "next_question": prompt, "allowed_actions": actions, "note": explanation,
            "read_only": True}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="خواندن وضعیت پرونده بدون وابستگی به سشن")
    parser.add_argument("--id", help="شناسه ایده، بدون URL")
    parser.add_argument("--root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    args = parser.parse_args()
    result = inspect(args.root, args.id)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["stage"] == "CONFLICT":
        raise SystemExit(2)
