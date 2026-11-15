# Attendance-tracker

## Setting up a new bootcamp

Edit the **EVENT SETTINGS** block at the top of `config.py` (sheet ID, city, start date, number of days, UTC offset) and push. Nothing needs changing on Render.

## Environment Variables

Create a `.env` file (or export these values in your shell) before running the app or the `scripts/send_congrats_emails.py` helper:

```
GOOGLE_PROJECT_ID=your_project_id
GOOGLE_PRIVATE_KEY_ID=your_private_key_id
GOOGLE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n"
GOOGLE_CLIENT_EMAIL=service-account@project.iam.gserviceaccount.com
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_X509_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/...

# Admin-only participant list. Leave unset to disable /api/participants entirely.
ADMIN_TOKEN=some-long-random-string
```

Fetch the participant list (admins only):

```
curl -H "X-Admin-Token: $ADMIN_TOKEN" https://<your-app>/api/participants
```

```

# Gmail SMTP configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_gmail_address@gmail.com
SMTP_PASSWORD=your_app_specific_password
SENDER_EMAIL=your_gmail_address@gmail.com
SMTP_USE_SSL=false

# Certificates sheet defaults (optional overrides)
CERTIFICATES_SHEET_NAME=certificates
CERTIFICATES_NAME_COLUMN=Full Name
CERTIFICATES_EMAIL_COLUMN=Email
CONGRATS_EMAIL_SUBJECT=Congratulations on completing the Uyo Lightning Bootcamp
```

For Gmail you must use an App Password (under Google Account → Security → App passwords) if two-factor authentication is enabled. Set `SMTP_USE_SSL=true` if you prefer port `465` and SSL instead of STARTTLS.

Dry run: python scripts/send_congrats_emails.py --dry-run --limit 3
Real send: python scripts/send_congrats_emails.py --subject "Congrats Builders!"
Target one recipient: add --only-email alice@example.com