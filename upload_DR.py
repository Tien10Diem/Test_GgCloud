from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import os
import io
import pandas as pd
import json
import gc

# ==== CẤU HÌNH ====
SERVICE_ACCOUNT_FILE = "service_account.json"  # 👈 Giữ nguyên
SCOPES = ['https://www.googleapis.com/auth/drive']
FOLDER_ID = "1M93UsOD7-Edm77CdZGDHkvR3aMmk9isP"  # 👈 Thay ID folder Drive của bạn
FILENAME = "crypto_full_data.csv"
LOCAL_NEW_FILE = "crypto_full_data.csv"

def get_existing_file_id(service):
    query = f"name='{FILENAME}' and '{FOLDER_ID}' in parents and trashed=false"
    results = service.files().list(
        q=query,
        supportsAllDrives=True,
        spaces='drive',
        fields='files(id, name)',
        includeItemsFromAllDrives=True
    ).execute()
    files = results.get('files', [])
    return files[0]['id'] if files else None

def download_drive_file(service, file_id):
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    fh.seek(0)
    return pd.read_csv(fh)

def upload_to_drive():
    if not os.path.exists(LOCAL_NEW_FILE):
        print(f"❌ Không tìm thấy file local: {LOCAL_NEW_FILE}")
        return

    # 🔐 Load credentials từ biến môi trường (JSON string)
    service_account_info = json.loads(os.environ["GDRIVE_KEY"])
    creds = service_account.Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
    service = build('drive', 'v3', credentials=creds)

    file_id = get_existing_file_id(service)
    print(f"📄 Đang kiểm tra file {FILENAME} trên Drive...")

    df_new = pd.read_csv(LOCAL_NEW_FILE)
    print(f"✅ Đã đọc file mới: {LOCAL_NEW_FILE} ({len(df_new)} dòng)")

    if file_id:
        print(f"📥 Đã tìm thấy file cũ (ID: {file_id}) – sẽ tải về & gộp dữ liệu")
        try:
            df_old = download_drive_file(service, file_id)
            df_combined = pd.concat([df_old, df_new], ignore_index=True)
            df_combined = df_combined.drop_duplicates(subset=["id", "time_collected"])
            df_combined.to_csv(LOCAL_NEW_FILE, index=False, encoding='utf-8-sig')
            print(f"🔄 Đã gộp data (tổng cộng: {len(df_combined)} dòng)")
        except Exception as e:
            print(f"⚠️ Không thể đọc file cũ – chỉ dùng data mới. Lý do: {e}")
    else:
        print("📄 Chưa có file cũ – sẽ tạo file mới.")

    media = MediaFileUpload(LOCAL_NEW_FILE, mimetype='text/csv', resumable=False)

    if file_id:
        service.files().update(
            fileId=file_id,
            media_body=media,
            supportsAllDrives=True
        ).execute()
        print("✅ Đã cập nhật file trên Drive.")
    else:
        file_metadata = {
            'name': FILENAME,
            'parents': [FOLDER_ID]
        }
        service.files().create(
            body=file_metadata,
            media_body=media,
            supportsAllDrives=True,
            fields='id'
        ).execute()
        print("✅ Đã tạo file mới trên Drive.")

    del df_new
    gc.collect()

if __name__ == "__main__":
    upload_to_drive()
