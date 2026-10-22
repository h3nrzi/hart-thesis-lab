"""هماهنگی نمای انسانی پرونده و INDEX.md در یک تغییر منطقی Git."""
from pathlib import Path
import re

def plan_status(root, idea, old_statuses, next_status):
    root = Path(root)
    case_path = root / "analyses" / idea / "case.md"
    index_path = root / "INDEX.md"
    case = case_path.read_text(encoding="utf-8")
    lines = case.splitlines()
    field = "- **وضعیت پرونده:** "
    matches = [i for i, line in enumerate(lines) if line.startswith(field)]
    if len(matches) != 1:
        raise ValueError("فیلد وضعیت پرونده یکتا نیست")
    old = lines[matches[0]][len(field):].strip()
    if old not in old_statuses:
        raise ValueError(f"تغییر وضعیت از {old!r} مجاز نیست")
    lines[matches[0]] = field + next_status
    updated_case = "\n".join(lines) + ("\n" if case.endswith("\n") else "")
    index = index_path.read_text(encoding="utf-8")
    rows = index.splitlines(keepends=True)
    found = 0
    for i, line in enumerate(rows):
        if f"](analyses/{idea}/case.md)" in line:
            chunks = line.split("|")
            if len(chunks) < 8 or chunks[5].strip() != old:
                raise ValueError("وضعیت INDEX.md با case.md ناسازگار است")
            chunks[5] = " " + next_status + " "
            rows[i] = "|".join(chunks)
            found += 1
    if found != 1:
        raise ValueError("پرونده در INDEX.md باید دقیقاً یک ردیف داشته باشد")
    return (case_path, updated_case), (index_path, "".join(rows))

def apply_status(planned):
    for path, content in planned:
        Path(path).write_text(content, encoding="utf-8")
