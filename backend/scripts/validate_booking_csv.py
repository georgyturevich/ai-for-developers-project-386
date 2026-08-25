#!/usr/bin/env python3
"""One-off CSV validator for booking bulk uploads.

Reads CSV with header: event_type_id,start,duration_minutes,guest_name,
guest_email,guest_comment and reports per-line errors. Validates against the
same rules the API enforces. Exits non-zero if any row is invalid.
"""

from __future__ import annotations

import csv
import sys
from dataclasses import dataclass, field
from datetime import datetime

import re
from email_validator import validate_email, EmailNotValidError

SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

EXPECTED_HEADER = [
    "event_type_id",
    "start",
    "duration_minutes",
    "guest_name",
    "guest_email",
    "guest_comment",
]


@dataclass
class RowErrors:
    row_number: int
    errors: list[str] = field(default_factory=list)


def validate_row(row_number: int, values: dict[str, str]) -> RowErrors:
    errors: list[str] = []

    event_type_id = values.get("event_type_id", "").strip()
    if not event_type_id:
        errors.append("event_type_id: empty")
    elif not SLUG_RE.match(event_type_id):
        errors.append(f"event_type_id: {event_type_id!r} is not a valid slug")

    start_raw = values.get("start", "").strip()
    if not start_raw:
        errors.append("start: empty")
    else:
        try:
            start = datetime.fromisoformat(start_raw.replace("Z", "+00:00"))
            if start.tzinfo is None:
                errors.append("start: must be timezone-aware (UTC)")
        except ValueError:
            errors.append(f"start: {start_raw!r} is not a valid ISO 8601 datetime")

    duration_raw = values.get("duration_minutes", "").strip()
    if not duration_raw:
        errors.append("duration_minutes: empty")
    else:
        try:
            duration = int(duration_raw)
            if duration <= 0:
                errors.append(f"duration_minutes: must be > 0, got {duration}")
        except ValueError:
            errors.append(f"duration_minutes: {duration_raw!r} is not an integer")

    if not values.get("guest_name", "").strip():
        errors.append("guest_name: empty")

    email = values.get("guest_email", "").strip()
    if not email:
        errors.append("guest_email: empty")
    else:
        try:
            validate_email(email, check_deliverability=False)
        except EmailNotValidError as exc:
            errors.append(f"guest_email: {email!r} is invalid ({exc})")

    return RowErrors(row_number=row_number, errors=errors)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: validate_booking_csv.py <file.csv>", file=sys.stderr)
        return 2

    path = sys.argv[1]
    problems = 0
    header_ok = True

    try:
        with open(path, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            header = reader.fieldnames or []
            if header != EXPECTED_HEADER:
                header_ok = False
                print(f"header: expected {EXPECTED_HEADER}, got {header}")
            for row_number, values in enumerate(reader, start=2):
                result = validate_row(row_number, values)
                if result.errors:
                    problems += 1
                    print(f"row {result.row_number}: " + "; ".join(result.errors))
    except FileNotFoundError:
        print(f"file not found: {path}", file=sys.stderr)
        return 2

    if not header_ok or problems:
        print(f"{problems} invalid row(s)")
        return 1

    print("all rows valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
