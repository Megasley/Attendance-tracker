# import argparse
# import os
# import smtplib
# import sys
# from dataclasses import dataclass
# from email.message import EmailMessage
# from typing import Iterable, List, Optional, Tuple

# import gspread
# from dotenv import load_dotenv
# from google.oauth2 import service_account

# load_dotenv()


# @dataclass
# class Participant:
#     name: str
#     email: str


# def get_gspread_client() -> gspread.Client:
#     scopes = ["https://www.googleapis.com/auth/spreadsheets"]
#     credentials_dict = {
#         "type": "service_account",
#         "project_id": os.getenv("GOOGLE_PROJECT_ID"),
#         "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
#         "private_key": os.getenv("GOOGLE_PRIVATE_KEY", "").replace("\\n", "\n"),
#         "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
#         "client_id": os.getenv("GOOGLE_CLIENT_ID"),
#         "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#         "token_uri": "https://oauth2.googleapis.com/token",
#         "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
#         "client_x509_cert_url": os.getenv("GOOGLE_CLIENT_X509_CERT_URL"),
#         "universe_domain": "googleapis.com",
#     }
#     missing = [k for k, v in credentials_dict.items() if not v]
#     if missing:
#         raise RuntimeError(f"Missing Google credential fields: {', '.join(missing)}")

#     creds = service_account.Credentials.from_service_account_info(
#         credentials_dict, scopes=scopes
#     )
#     return gspread.authorize(creds)


# def fetch_participants(sheet_name: str, column_email: str, column_name: Optional[str]) -> List[Participant]:
#     client = get_gspread_client()
#     spreadsheet_id = os.getenv("GOOGLE_SHEETS_ID")
#     if not spreadsheet_id:
#         raise RuntimeError("GOOGLE_SHEETS_ID is not set.")

#     sheet = client.open_by_key(spreadsheet_id).worksheet(sheet_name)
#     records = sheet.get_all_records()
#     participants: List[Participant] = []

#     for row in records:
#         email = row.get(column_email) or row.get(column_email.lower())
#         if not email:
#             continue
#         name = ""
#         if column_name:
#             name = row.get(column_name) or row.get(column_name.lower()) or ""
#         if not name:
#             first = row.get("First Name") or row.get("first name") or ""
#             last = row.get("Last Name") or row.get("last name") or ""
#             name = f"{first} {last}".strip()
#         if not name:
#             name = email.split("@", 1)[0]
#         participants.append(Participant(name=name.strip(), email=email.strip()))

#     return participants


# def build_email_contents(participant: Participant) -> Tuple[str, str]:
#     display_name = participant.name or "builder"
#     text_body = f"""Hello {display_name} !!!!

# I want to congratulate you once again for completing the Uyo Lightning Developer Bootcamp. You showed real commitment throughout the sessions, and it means a lot that you dedicated your time and energy to learning and building with us.

# Your journey as a Bitcoin and Lightning developer is only beginning. I encourage you to take the next step by joining the Btrust Builders community. It gives you access to mentors, learning resources, grants, open source projects, and a strong network of builders across Africa and beyond. It is one of the best ways to grow fast and stay active in the ecosystem.

# If you want to go even deeper, you can also sign up for one of the Btrust Pathways. They offer guided learning tracks designed to help you level up.

# Apply for Btrust Pathways here: https://btrust.homerun.co/btrust-builders-application/en?ref=africafreerouting

# To receive your certificate, you must complete the required forms. Please fill them out carefully, especially your name, as it will appear exactly the same on your certificate.

# Here are the forms:
# Profile form (required for certificate): https://freerouting.africa/profile/
# Feedback form: https://forms.gle/VkCDuZ1nfyM5KdEt6

# I would also love to hear your thoughts about your experience, so your feedback means a lot and helps us improve future bootcamps.

# Recommended order:
# 1. Btrust Pathways
# 2. Profile Form
# 3. Feedback Form

# Thank you once again for being part of this amazing journey. I am proud of you and excited to see everything you will build from here.

# Regards,
# Megasley
# """

#     html_body = f"""<p>Hello {display_name} !!!!</p>
# <p>I want to congratulate you once again for completing the Uyo Lightning Developer Bootcamp. You showed real commitment throughout the sessions, and it means a lot that you dedicated your time and energy to learning and building with us.</p>
# <p>Your journey as a Bitcoin and Lightning developer is only beginning. I encourage you to take the next step by joining the Btrust Builders community. It gives you access to mentors, learning resources, grants, open source projects, and a strong network of builders across Africa and beyond. It is one of the best ways to grow fast and stay active in the ecosystem.</p>
# <p>If you want to go even deeper, you can also sign up for one of the Btrust Pathways. They offer guided learning tracks designed to help you level up.</p>
# <p>Apply for Btrust Pathways here: <a href="https://btrust.homerun.co/btrust-builders-application/en?ref=africafreerouting">Btrust Pathways Application</a></p>
# <p>To receive your certificate, you must complete the required forms. Please fill them out carefully, especially your name, as it will appear exactly the same on your certificate.</p>
# <p>Here are the forms:</p>
# <ul>
#   <li>Profile form (required for certificate): <a href="https://freerouting.africa/profile/">https://freerouting.africa/profile/</a></li>
#   <li>Feedback form: <a href="https://forms.gle/VkCDuZ1nfyM5KdEt6">https://forms.gle/VkCDuZ1nfyM5KdEt6</a></li>
# </ul>
# <p>I would also love to hear your thoughts about your experience, so your feedback means a lot and helps us improve future bootcamps.</p>
# <p>Recommended order:</p>
# <ol>
#   <li>Btrust Pathways</li>
#   <li>Profile Form</li>
#   <li>Feedback Form</li>
# </ol>
# <p>Thank you once again for being part of this amazing journey. I am proud of you and excited to see everything you will build from here.</p>
# <p>Regards,<br/>Megasley</p>
# """

#     return text_body, html_body


# def send_email(participant: Participant, subject: str, sender: str, smtp_host: str, smtp_port: int,
#                username: str, password: str, use_tls: bool) -> None:
#     message = EmailMessage()
#     message["Subject"] = subject
#     message["From"] = sender
#     message["To"] = participant.email
#     text_body, html_body = build_email_contents(participant)
#     message.set_content(text_body)
#     message.add_alternative(html_body, subtype="html")

#     if use_tls:
#         with smtplib.SMTP(smtp_host, smtp_port) as smtp:
#             smtp.starttls()
#             smtp.login(username, password)
#             smtp.send_message(message)
#     else:
#         with smtplib.SMTP_SSL(smtp_host, smtp_port) as smtp:
#             smtp.login(username, password)
#             smtp.send_message(message)


# def parse_args() -> argparse.Namespace:
#     parser = argparse.ArgumentParser(description="Send personalized bootcamp congratulatory emails.")
#     parser.add_argument("--sheet-name", default=os.getenv("CERTIFICATES_SHEET_NAME", "Certificates"))
#     parser.add_argument("--name-column", default=os.getenv("CERTIFICATES_NAME_COLUMN", "Full Name"),
#                         help="Column header containing the participant name.")
#     parser.add_argument("--email-column", default=os.getenv("CERTIFICATES_EMAIL_COLUMN", "Email"),
#                         help="Column header containing recipient email.")
#     parser.add_argument("--subject", default=os.getenv("CONGRATS_EMAIL_SUBJECT",
#                                                        "Congratulations on completing the Uyo Lightning Bootcamp"))
#     parser.add_argument("--limit", type=int, help="Optional cap on number of emails to send.")
#     parser.add_argument("--only-email", help="Send to a single email address for testing.")
#     parser.add_argument("--dry-run", action="store_true", help="Print the emails instead of sending.")
#     return parser.parse_args()


# def main():
#     args = parse_args()

#     smtp_host = os.getenv("SMTP_HOST")
#     smtp_port = int(os.getenv("SMTP_PORT", "587"))
#     smtp_username = os.getenv("SMTP_USERNAME")
#     smtp_password = os.getenv("SMTP_PASSWORD")
#     sender_email = os.getenv("SENDER_EMAIL") or smtp_username
#     use_tls = os.getenv("SMTP_USE_SSL", "false").lower() not in {"1", "true", "yes"}

#     if not args.dry_run and not all([smtp_host, smtp_username, smtp_password, sender_email]):
#         raise RuntimeError("SMTP credentials are incomplete. Set SMTP_HOST, SMTP_USERNAME, SMTP_PASSWORD, and SENDER_EMAIL.")

#     participants = fetch_participants(args.sheet_name, args.email_column, args.name_column)

#     if args.only_email:
#         participants = [p for p in participants if p.email.lower() == args.only_email.lower()]

#     if args.limit:
#         participants = participants[: args.limit]

#     if not participants:
#         print("No participants found. Nothing to send.")
#         return

#     for participant in participants:
#         if args.dry_run:
#             print(f"--- DRY RUN: {participant.email} ---")
#             text_body, html_body = build_email_contents(participant)
#             print(text_body)
#             print("\n--- HTML VERSION ---\n")
#             print(html_body)
#             print()
#             continue

#         send_email(
#             participant=participant,
#             subject=args.subject,
#             sender=sender_email,
#             smtp_host=smtp_host,
#             smtp_port=smtp_port,
#             username=smtp_username,
#             password=smtp_password,
#             use_tls=use_tls,
#         )
#         print(f"Sent to {participant.email}")


# if __name__ == "__main__":
#     try:
#         main()
#     except Exception as exc:
#         print(f"Error: {exc}", file=sys.stderr)
#         sys.exit(1)

