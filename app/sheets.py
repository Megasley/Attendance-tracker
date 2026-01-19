from google.oauth2 import service_account
import gspread
from config import Config
from datetime import datetime
import os
from dotenv import load_dotenv
import re

load_dotenv()

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
    """Map current date to Day number based on event dates
    Day 1 = January 19, 2026
    Day 2 = January 20, 2026
    Day 3 = January 21, 2026
    Day 4 = January 22, 2026
    Day 5 = January 23, 2026
    """
    event_dates = {
        datetime(2026, 1, 19).date(): 1,
        datetime(2026, 1, 20).date(): 2,
        datetime(2026, 1, 21).date(): 3,
        datetime(2026, 1, 22).date(): 4,
        datetime(2026, 1, 23).date(): 5,
    }
    return event_dates.get(current_date)

def verify_access_code(access_code):
    try:
        # Set up authentication
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
        
        # Open the spreadsheet and select the specific worksheet
        spreadsheet = client.open_by_key(Config.GOOGLE_SHEETS_ID)
        sheet = spreadsheet.worksheet("Attendance")
        
        # Get all values
        all_values = sheet.get_all_values()
        
        if not all_values or len(all_values) < 1:
            return {'success': False, 'message': 'Spreadsheet is empty'}
        
        # Get current date and determine which day it corresponds to
        current_date = datetime.now().date()
        day_number = get_day_for_date(current_date)
        
        if day_number is None:
            return {'success': False, 'message': f'Check-in is only available on event dates (January 19-23, 2026). Today is {current_date.strftime("%B %d, %Y")}.'}
        
        # Get header row (first row)
        header_row = all_values[0]
        
        # Find the Day column that matches today's day number
        # Structure: First Name, Last Name, Email, Phone Number, CV, Day 1, Day 2, Day 3, Day 4, Day 5
        day_column_info = None  # (column_index, column_letter, day_number)
        
        for col_index, header_value in enumerate(header_row):
            header_day_number = is_day_column(header_value)
            if header_day_number == day_number:
                column_letter = column_number_to_letter(col_index + 1)  # +1 because Sheets is 1-based
                day_column_info = (col_index, column_letter, day_number)
                break
        
        if day_column_info is None:
            return {'success': False, 'message': f'Day {day_number} column not found in spreadsheet header'}
        
        col_index, column_letter, day_number = day_column_info
        
        # Find the user by email (access_code) in column C (index 2)
        user_name = "User"
        user_row_index = None
        
        for index, row in enumerate(all_values[1:], start=2):  # Start=2 because we skip header and Google Sheets is 1-based
            if len(row) >= 3 and row[2].lower() == access_code.lower():  # Column C (index 2) is Email
                user_name = row[0] if len(row) > 0 and row[0] else "User"
                if len(row) > 1 and row[1]:  # Add last name if available
                    user_name = f"{user_name} {row[1]}"
                user_row_index = index
                break
        
        if user_row_index is None:
            return {'success': False, 'message': 'Email not found in the system'}
        
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
        
        return {'success': True, 'message': f'{user_name.title()}'}
        
    except Exception as e:
        print(f"Error: {str(e)}")  # Added for debugging
        import traceback
        traceback.print_exc()
        return {'success': False, 'message': str(e)}