import streamlit as st
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from oauth2client.service_account import ServiceAccountCredentials
import os
import datetime

# Google Drive setup
FOLDER_ID = "13hG9ayDAHfK9MdVXUQwAYyZlUqWMKKYK"  # your shared Google Drive folder ID
CREDS_FILE = "credentials.json"

scope = ['https://www.googleapis.com/auth/drive']
gauth = GoogleAuth()
gauth.credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, scope)
drive = GoogleDrive(gauth)

# Streamlit UI
st.title("Meter Replacement Photo Upload")

technician = st.text_input("Technician Name")
zone = st.selectbox("Zone", ["NZ", "CZ", "SZ", "MCZ", "SCZ", "EZ"])
locality = st.text_input("Locality")
building = st.text_input("Building Name")
remark = st.text_area("Remarks")
uploaded_files = st.file_uploader("Upload Old Meter Photos", accept_multiple_files=True, type=["jpg", "jpeg", "png"])

if st.button("Upload Photos"):
    if not all([technician, zone, locality, building, uploaded_files]):
        st.warning("Please fill all required fields and upload at least one photo.")
    else:
        # Check or create subfolder for building
        query = f"'{FOLDER_ID}' in parents and title = '{building}' and mimeType = 'application/vnd.google-apps.folder' and trashed=false"
        folder_list = drive.ListFile({'q': query}).GetList()

        if folder_list:
            subfolder = folder_list[0]
        else:
            subfolder_metadata = {'title': building, 'parents': [{'id': FOLDER_ID}], 'mimeType': 'application/vnd.google-apps.folder'}
            subfolder = drive.CreateFile(subfolder_metadata)
            subfolder.Upload()

        for file in uploaded_files:
            now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{technician}_{zone}_{locality}_{now}_{file.name}"
            gfile = drive.CreateFile({'title': filename, 'parents': [{'id': subfolder['id']}]})
            gfile.SetContentString(file.getvalue().decode("ISO-8859-1"))
            gfile.Upload()

        st.success("All photos uploaded successfully!")
