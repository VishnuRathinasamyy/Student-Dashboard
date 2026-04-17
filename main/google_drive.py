# app_name/google_drive.py
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
from django.conf import settings

SCOPES = ['https://www.googleapis.com/auth/drive.file']  # limited scope
SERVICE_ACCOUNT_FILE = getattr(settings, 'GOOGLE_SERVICE_ACCOUNT_FILE', 'credentials/service_account.json')
FOLDER_ID = getattr(settings, 'GOOGLE_DRIVE_FOLDER_ID', None)

def upload_to_drive(django_file, filename, folder_id=None):
    """
    Uploads a Django UploadedFile (from request.FILES) to Google Drive and returns webViewLink.
    """
    folder_id = folder_id or FOLDER_ID
    if not folder_id:
        raise ValueError("FOLDER_ID is not configured.")

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build('drive', 'v3', credentials=credentials, cache_discovery=False)

    file_metadata = {
        'name': filename,
        'parents': [folder_id]
    }

    # django_file might be InMemoryUploadedFile or TemporaryUploadedFile
    # read content into BytesIO
    file_stream = io.BytesIO(django_file.read())
    media = MediaIoBaseUpload(file_stream, mimetype=django_file.content_type)

    created = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id, webViewLink, mimeType, name'
    ).execute()

    # Optionally make file publicly readable (not recommended) or leave private.
    return created.get('webViewLink')

from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_info(GOOGLE_CREDENTIALS)