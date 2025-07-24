import streamlit as st
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
import tempfile

# --- Google Drive Authentication ---
gauth = GoogleAuth()
gauth.LoadCredentialsFile("credentials.json")

if gauth.credentials is None:
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    gauth.Refresh()
else:
    gauth.Authorize()

gauth.SaveCredentialsFile("credentials.json")
drive = GoogleDrive(gauth)

# --- Configuration ---
PARENT_FOLDER_ID = '13hG9ayDAHfK9MdVXUQwAYyZlUqWMKKYK'  # <- Replace with your actual Drive folder ID

# --- Streamlit UI ---
st.title("Meter Photo Upload")

technician = st.text_input("Technician Name")
locality = st.text_input("Locality")
building = st.text_input("Building Name")
remark = st.text_area("Remark")
photos = st.file_uploader("Upload Old Meter Photos", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if st.button("Upload to Drive"):
    if not technician or not locality or not building or not photos:
        st.error("Please fill all fields and upload at least one photo.")
    else:
        # Create subfolder in Drive for this building
        folder_metadata = {
            'title': building,
            'parents': [{'id': PARENT_FOLDER_ID}],
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = drive.CreateFile(folder_metadata)
        folder.Upload()
        st.success(f"Drive folder '{building}' created.")

        # Upload photos
        for photo in photos:
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(photo.read())
                file_drive = drive.CreateFile({
                    'title': photo.name,
                    'parents': [{'id': folder['id']}]
                })
                file_drive.SetContentFile(tmp_file.name)
                file_drive.Upload()
                os.unlink(tmp_file.name)

        st.success("Photos uploaded successfully.")
