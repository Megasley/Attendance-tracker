import os
from datetime import date, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()


# ============================================================
# EVENT SETTINGS: edit these for each bootcamp, then push.
# (Not read from .env / Render, so there's only one place to change them.)
# ============================================================
GOOGLE_SHEETS_ID = '1ZLRzb7NzcBYS-HcYQY5a7iX0Eja0Z-xUM0TsfL76FDk'
EVENT_CITY = 'Dakar'
EVENT_START_DATE = date(2026, 11, 16)   # Day 1
EVENT_DAYS = 5                          # sheet needs "Day 1" ... "Day 4" columns
EVENT_UTC_OFFSET = 1                    # Dakar 0, Lagos 1, Kigali 2, Addis Ababa / Dar es Salaam 3
# ============================================================


class Config:
    SECRET_KEY = os.urandom(24)
    GOOGLE_SHEETS_ID = GOOGLE_SHEETS_ID.strip()

    # Secret, so it stays in .env / Render. If unset, /api/participants is disabled.
    ADMIN_TOKEN = os.getenv('ADMIN_TOKEN', '')

    EVENT_CITY = EVENT_CITY
    EVENT_START_DATE = EVENT_START_DATE
    EVENT_DAYS = EVENT_DAYS
    EVENT_UTC_OFFSET = EVENT_UTC_OFFSET
    EVENT_TZ = timezone(timedelta(hours=EVENT_UTC_OFFSET))
    EVENT_END_DATE = EVENT_START_DATE + timedelta(days=EVENT_DAYS - 1)


def event_date_range_text():
    """Human-readable event dates, e.g. 'November 17-20, 2026'."""
    start, end = Config.EVENT_START_DATE, Config.EVENT_END_DATE
    if start == end:
        return f"{start:%B} {start.day}, {start.year}"
    if (start.year, start.month) == (end.year, end.month):
        return f"{start:%B} {start.day}-{end.day}, {start.year}"
    if start.year == end.year:
        return f"{start:%B} {start.day} - {end:%B} {end.day}, {start.year}"
    return f"{start:%B} {start.day}, {start.year} - {end:%B} {end.day}, {end.year}"
