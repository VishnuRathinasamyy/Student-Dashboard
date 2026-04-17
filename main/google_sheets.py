import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from googleapiclient.discovery import build
from google.oauth2 import service_account
from django.contrib.auth.models import User
from main.models import Student  # Replace main with your app name

# Path to your service account JSON key
SERVICE_ACCOUNT_FILE = 'path/to/service-account.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# Your Google Sheet ID
SPREADSHEET_ID = 'YOUR_SPREADSHEET_ID'
RANGE_NAME = 'Form Responses 1!A:D'  # Adjust depending on your sheet

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

service = build('sheets', 'v4', credentials=credentials)
sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                            range=RANGE_NAME).execute()
values = result.get('values', [])

if not values:
    print('No data found.')
else:
    # Skip header row
    for row in values[1:]:
        # Adjust indexes according to sheet columns
        name = row[0]
        email = row[1]
        phone = row[2]
        course_name = row[3].lower().replace(' ', '_')  # Make key match choices

        # Check if user exists
        user, created = User.objects.get_or_create(
            username=email,
            defaults={'first_name': name.split(' ')[0], 
                      'last_name': ' '.join(name.split(' ')[1:]), 
                      'email': email}
        )

        # Check if student exists
        student, created = Student.objects.get_or_create(
            user=user,
            defaults={
                'phone': phone,
                'course': course_name
            }
        )

        if created:
            print(f"Created student: {student}")
        else:
            print(f"Student already exists: {student}")
