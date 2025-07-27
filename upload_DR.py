import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# === CONFIG ===
SERVICE_ACCOUNT_FILE = 'service_account.json'
SCOPES = ['https://www.googleapis.com/auth/drive']
FOLDER_ID = '1gf3MFOaHj75BzhLj8O7jN0utcwo_4jE7'
FILE_NAME = 'crypto_full_data.csv'

def check_folder_access(service, folder_id):
    try:
        folder = service.files().get(fileId=folder_id, fields="id, name").execute()
        print(f"📁 Truy cập thư mục thành công: {folder['name']} ({folder['id']})")
    except HttpError as e:
        print(f"❌ Không thể truy cập thư mục: {e}")
        raise

def find_file_id(service, filename, folder_id):
    query = f"name='{filename}' and '{folder_id}' in parents and trashed=false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])
    if files:
        return files[0]['id']
    return None

def upload_to_drive():
    print("🚀 Bắt đầu upload lên Google Drive...")

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=credentials)

    # Test quyền truy cập folder
    check_folder_access(service, FOLDER_ID)

    media = MediaFileUpload(FILE_NAME, mimetype='text/csv', resumable=True)
    existing_file_id = find_file_id(service, FILE_NAME, FOLDER_ID)

    try:
        if existing_file_id:
            print("🔄 File đã tồn tại, đang cập nhật...")
            updated = service.files().update(
                fileId=existing_file_id,
                media_body=media,
                fields='id'
            ).execute()
            print(f"✅ Đã cập nhật file: {updated.get('id')}")
        else:
            print("📄 File chưa tồn tại, tạo mới...")
            file_metadata = {
                'name': FILE_NAME,
                'parents': [FOLDER_ID]
            }
            created = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            print(f"✅ Đã tạo file mới: {created.get('id')}")
    except HttpError as e:
        print(f"❌ Lỗi khi upload: {e}")
        raise

if __name__ == '__main__':
    upload_to_drive()
