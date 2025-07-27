from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
import json

def upload_to_drive():
    # Tải credentials từ biến môi trường hoặc file
    creds = service_account.Credentials.from_service_account_file(
        'service_account.json',
        scopes=['https://www.googleapis.com/auth/drive']
    )

    # Tạo dịch vụ Drive
    service = build('drive', 'v3', credentials=creds)

    # Đường dẫn tệp cần upload
    file_path = 'crypto_full_data.csv'

    # Cấu hình metadata cho file mới
    file_metadata = {
        'name': 'crypto_full_data.csv',
        'parents': ['1M93UsOD7-Edm77CdZGDHkvR3aMmk9isP']  # Folder ID
    }

    # Cấu hình nội dung file
    media = MediaFileUpload(file_path, mimetype='text/csv')

    # Upload file
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    print(f"✅ File uploaded. File ID: {file.get('id')}")
