from google.oauth2 import service_account
import gspread
from config import Config
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

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
        
        # Skip header row and check values
        current_date = datetime.now().date()
        for index, row in enumerate(all_values[1:], start=2):  # Start=2 because we skip header and Google Sheets is 1-based
            if len(row) >= 3 and row[2] == access_code:  # Column C (index 2)
                # Get the user's name from column A
                user_name = row[0] if len(row) > 0 else "User"
                
                if current_date == datetime(2025, 4, 9).date():
                    cell = f'F{index}'
                    sheet.update(cell, True)  # Update to TRUE
                    cell_range = f'A{index}:F{index}'
                    sheet.format(cell_range, {
                        "backgroundColor": {
                            "red": 0.85,
                            "green": 0.92,
                            "blue": 0.85
                        }
                    })
                elif current_date == datetime(2025, 4, 10).date():
                    cell = f'G{index}'
                    sheet.update(cell, True)  # Update to TRUE
                    cell_range = f'A{index}:G{index}'
                    sheet.format(cell_range, {
                        "backgroundColor": {
                            "red": 0.85,
                            "green": 0.92,
                            "blue": 0.85
                        }
                    })
                elif current_date == datetime(2025, 4, 11).date():
                    cell = f'H{index}'
                    sheet.update(cell, True)  # Update to TRUE
                    cell_range = f'A{index}:H{index}'
                    sheet.format(cell_range, {
                        "backgroundColor": {
                            "red": 0.85,
                            "green": 0.92,
                            "blue": 0.85
                        }
                    })
                elif current_date == datetime(2025, 4, 12).date():
                    cell = f'I{index}'
                    sheet.update(cell, True)  # Update to TRUE
                    cell_range = f'A{index}:I{index}'
                    sheet.format(cell_range, {
                        "backgroundColor": {
                            "red": 0.85,
                            "green": 0.92,
                            "blue": 0.85
                        }
                    })
                
                return {'success': True, 'message': user_name}
        
    except Exception as e:
        print(f"Error: {str(e)}")  # Added for debugging
        return {'success': False, 'message': str(e)}