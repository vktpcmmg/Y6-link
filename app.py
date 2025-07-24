import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
import datetime

# --- CONFIG ---
FOLDER_ID = "13hG9ayDAHfK9MdVXUQwAYyZlUqWMKKYK"  # Root Google Drive Folder
CREDS_FILE = "credentials.json"

# --- AUTH ---
SCOPES = ['https://www.googleapis.com/auth/drive']
credentials = service_account.Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)

# --- FUNCTIONS ---
def create_or_get_folder(name, parent_id):
    query = f"'{parent_id}' in parents and name = '{name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    folders = results.get('files', [])

    if folders:
        return folders[0]['id']
    else:
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id]
        }
        folder = drive_service.files().create(body=file_metadata, fields='id').execute()
        return folder.get('id')

def upload_file_to_folder(file, filename, folder_id):
    file_stream = io.BytesIO(file.read())
    media = MediaIoBaseUpload(file_stream, mimetype='image/jpeg', resumable=True)

    file_metadata = {
        'name': filename,
        'parents': [folder_id]
    }

    uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return uploaded_file.get('id')

# --- UI ---
st.title("Meter Replacement Photo Upload")

technician = st.text_input("Technician Name")
zone = st.selectbox("Zone", ["NZ", "CZ", "SZ", "MCZ", "SCZ", "EZ"])
locality = st.text_input("Locality")
building = st.text_input("Building Name")
remarks = st.text_area("Remarks (optional)")
photos = st.file_uploader("Upload Old Meter Photos", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)

if st.button("Upload"):
    if not technician or not zone or not locality or not building or not photos:
        st.warning("All fields except remarks are required.")
    else:
        folder_id = create_or_get_folder(building, FOLDER_ID)

        for photo in photos:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            file_name = f"{technician}_{zone}_{locality}_{timestamp}_{photo.name}"
            upload_file_to_folder(photo, file_name, folder_id)

        st.success("Photos uploaded successfully.")
