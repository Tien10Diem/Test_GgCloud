from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
from datetime import datetime

# === CONFIG ===
SERVICE_ACCOUNT_FILE = "service_account.json"  # 🔧 Dùng file thay vì biến môi trường
SCOPES = ['https://www.googleapis.com/auth/drive']
DRIVE_FOLDER_ID = '1M93UsOD7-Edm77CdZGDHkvR3aMmk9isP'  # Thay bằng ID thư mục Google Drive của bạn

def upload_to_drive():
    print("🚀 Bắt đầu upload lên Google Drive...")

    # Load credentials từ file
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )

    service = build('drive', 'v3', credentials=credentials)

    file_name = 'crypto_full_data.csv'
    file_metadata = {
        'name': f'crypto_full_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
        'parents': [DRIVE_FOLDER_ID]
    }
    media = MediaFileUpload(file_name, mimetype='text/csv')

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    print(f"✅ Đã upload file lên Drive với ID: {file.get('id')}")

if __name__ == "__main__":
    upload_to_drive()
