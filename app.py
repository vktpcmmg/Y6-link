import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Title
st.title("📂 Google Drive Folder Browser")

# Define scope for Google Drive
SCOPES = ['https://www.googleapis.com/auth/drive']

# Load service account info from Streamlit secrets
creds = service_account.Credentials.from_service_account_info(
    st.secrets["google_service_account"], scopes=SCOPES
)

# Initialize Google Drive API
drive_service = build('drive', 'v3', credentials=creds)

# Replace with your shared folder ID (Y6 Photos)
FOLDER_ID = "13hG9ayDAHfK9MdVXUQwAYyZlUqWMKKYK"

# Function to list files from folder
def list_files_from_folder(folder_id):
    query = f"'{folder_id}' in parents and trashed = false"
    results = drive_service.files().list(
        q=query,
        fields="files(id, name, mimeType, webViewLink)"
    ).execute()
    return results.get('files', [])

# Get files from folder
files = list_files_from_folder(FOLDER_ID)

# Show files in Streamlit
if not files:
    st.warning("No files found in the Drive folder.")
else:
    st.subheader("Files in Drive Folder:")
    for file in files:
        st.markdown(f"📎 [{file['name']}]({file['webViewLink']})")
