import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# === CONFIG ===
SERVICE_ACCOUNT_FILE = 'service_account.json'  # hoặc thay bằng biến môi trường nếu muốn
SCOPES = ['https://www.googleapis.com/auth/drive']
FOLDER_ID = '1gf3MFOaHj75BzhLj8O7jN0utcwo_4jE7'  # Folder ID trên Google Drive
FILE_NAME = 'crypto_full_data.csv'  # Tên file cần upload

def upload_to_drive():
    print("🚀 Bắt đầu upload lên Google Drive...")

    # Load service account key từ file
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    # Tạo service Drive
    service = build('drive', 'v3', credentials=credentials)

    # Metadata của file (gồm thư mục cha)
    file_metadata = {
        'name': FILE_NAME,
        'parents': [FOLDER_ID]
    }

    # Chuẩn bị file để upload
    media = MediaFileUpload(FILE_NAME, mimetype='text/csv', resumable=True)

    # Tạo file mới (KHÔNG dùng update nếu bạn không biết file ID cũ)
    uploaded_file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    print(f"✅ Đã upload file với ID: {uploaded_file.get('id')}")

if __name__ == '__main__':
    upload_to_drive()
