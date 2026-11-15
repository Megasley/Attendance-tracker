from google.oauth2 import service_account
import gspread
from config import Config, event_date_range_text
from datetime import datetime
import logging
import os
from dotenv import load_dotenv
import re

load_dotenv()

logger = logging.getLogger(__name__)

GENERIC_ERROR = 'Something went wrong while checking you in. Please try again or ask an organiser for help.'

def get_attendance_sheet():
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    credentials_dict = {
        "type": "service_account",
        "project_id": os.getenv("GOOGLE_PROJECT_ID"),
        "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
        "private_key": os.getenv("GOOGLE_PRIVATE_KEY").replace('\\n', '\n'),
        "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": os.getenv("GOOGLE_CLIENT_X509_CERT_URL"),
        "universe_domain": "googleapis.com"
    }
    creds = service_account.Credentials.from_service_account_info(
        credentials_dict,
        scopes=scopes
    )
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(Config.GOOGLE_SHEETS_ID)
    return spreadsheet.worksheet("Attendance")

def normalize_header(header_value):
    """Convert a sheet header into a JSON-friendly key."""
    return re.sub(r'[^a-z0-9]+', '_', header_value.strip().lower()).strip('_')

def column_number_to_letter(n):
    """Convert a column number to a letter (e.g., 1 -> A, 27 -> AA)"""
    result = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        result = chr(65 + remainder) + result
    return result

def is_day_column(header_value):
    """Check if header is a Day column (Day 1, Day 2, etc.)"""
    if not header_value:
        return False
    header_lower = header_value.strip().lower()
    # Match "Day 1", "Day 2", etc. or "Day1", "Day2", etc.
    match = re.match(r'day\s*(\d+)', header_lower)
    if match:
        return int(match.group(1))
    return False

def get_day_for_date(current_date):
    """Map a date to its event Day number (1-based), or None if it's not an event day.
    Event dates come from EVENT_START_DATE and EVENT_DAYS in the config."""
    day_number = (current_date - Config.EVENT_START_DATE).days + 1
    if 1 <= day_number <= Config.EVENT_DAYS:
        return day_number
    return None

CHECKED_IN_VALUES = {'true', 'yes', 'y', '1', 'x', '\u2713', '\u2714'}

def is_checked_in(cell_value):
    return str(cell_value).strip().lower() in CHECKED_IN_VALUES

def get_bootcamp_participants():
    try:
        sheet = get_attendance_sheet()
        all_values = sheet.get_all_values()

        if not all_values or len(all_values) < 1:
            return {'success': False, 'message': 'Spreadsheet is empty'}

        headers = [normalize_header(header) for header in all_values[0]]
        participants = []

        for row_number, row in enumerate(all_values[1:], start=2):
            if not any(cell.strip() for cell in row):
                continue

            participant = {'row_number': row_number}
            for index, header in enumerate(headers):
                if not header:
                    continue
                participant[header] = row[index] if index < len(row) else ''

            participants.append(participant)

        return {
            'success': True,
            'count': len(participants),
            'participants': participants
        }

    except Exception:
        logger.exception("Failed to load participants")
        return {'success': False, 'message': 'Could not load participants.'}

def verify_access_code(access_code):
    access_code = (access_code or '').strip().lower()
    try:
        sheet = get_attendance_sheet()
        
        # Get all values
        all_values = sheet.get_all_values()
        
        if not all_values or len(all_values) < 1:
            return {'success': False, 'message': 'Spreadsheet is empty'}
        
        # Get current date in the event's local time and determine which day it corresponds to
        current_date = datetime.now(Config.EVENT_TZ).date()
        day_number = get_day_for_date(current_date)
        
        if day_number is None:
            return {'success': False, 'message': f'Check-in is only available on event dates ({event_date_range_text()}). Today is {current_date.strftime("%B %d, %Y")}.'}
        
        # Get header row (first row)
        header_row = all_values[0]
        
        # Find the Day column that matches today's day number
        # Structure: First Name, Last Name, Email, Phone Number, CV, Day 1, Day 2, ... Day N
        day_column_info = None  # (column_index, column_letter, day_number)
        
        for col_index, header_value in enumerate(header_row):
            header_day_number = is_day_column(header_value)
            if header_day_number == day_number:
                column_letter = column_number_to_letter(col_index + 1)  # +1 because Sheets is 1-based
                day_column_info = (col_index, column_letter, day_number)
                break
        
        if day_column_info is None:
            logger.error("Day %s column not found in spreadsheet header: %r", day_number, header_row)
            return {'success': False, 'message': "Check-in isn't set up for today yet. Please ask an organiser for help."}
        
        col_index, column_letter, day_number = day_column_info
        
        # Find the user by email (access_code) in column C (index 2)
        user_name = "User"
        user_row_index = None
        
        for index, row in enumerate(all_values[1:], start=2):  # Start=2 because we skip header and Google Sheets is 1-based
            if len(row) >= 3 and row[2].strip().lower() == access_code:  # Column C (index 2) is Email
                user_name = row[0] if len(row) > 0 and row[0] else "User"
                if len(row) > 1 and row[1]:  # Add last name if available
                    user_name = f"{user_name} {row[1]}"
                user_row_index = index
                break
        
        if user_row_index is None:
            return {'success': False, 'message': 'Email not found in the system'}
        
        # Don't re-write the sheet if they've already checked in today
        user_row = all_values[user_row_index - 1]
        if col_index < len(user_row) and is_checked_in(user_row[col_index]):
            return {
                'success': True,
                'already_checked_in': True,
                'name': user_name.title(),
                'message': f'{user_name.title()}',
            }
        
        # Update the attendance cell to TRUE for today's day
        cell = f'{column_letter}{user_row_index}'
        sheet.update(cell, True)
        
        # Apply green background color to the row from column A to the checked day column
        cell_range = f'A{user_row_index}:{column_letter}{user_row_index}'
        sheet.format(cell_range, {
            "backgroundColor": {
                "red": 0.85,
                "green": 0.92,
                "blue": 0.85
            }
        })
        
        return {
            'success': True,
            'already_checked_in': False,
            'name': user_name.title(),
            'message': f'{user_name.title()}',
        }
        
    except Exception:
        logger.exception("Check-in failed")
        return {'success': False, 'message': GENERIC_ERROR}