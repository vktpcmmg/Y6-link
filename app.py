import streamlit as st
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
from datetime import datetime

# Google Drive Authentication
gauth = GoogleAuth()
gauth.LocalWebserverAuth()
drive = GoogleDrive(gauth)

# Replace with your main folder ID in Google Drive
PARENT_FOLDER_ID = '13hG9ayDAHfK9MdVXUQwAYyZlUqWMKKYK'

# Create folder inside Google Drive
def create_drive_folder(folder_name, parent_id):
    folder_metadata = {
        'title': folder_name,
        'parents': [{'id': parent_id}],
        'mimeType': 'application/vnd.google-apps.folder'
    }
    folder = drive.CreateFile(folder_metadata)
    folder.Upload()
    return folder['id']

# Upload file to Google Drive
def upload_file_to_drive(file, folder_id):
    filename = file.name
    filepath = os.path.join("/tmp", filename)
    with open(filepath, "wb") as f:
        f.write(file.getvalue())

    drive_file = drive.CreateFile({'title': filename, 'parents': [{'id': folder_id}]})
    drive_file.SetContentFile(filepath)
    drive_file.Upload()
    os.remove(filepath)

# Create metadata text file and upload it
def upload_metadata(folder_id, technician, zone, locality, site_name, remark):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content = f"""Technician: {technician}
Zone: {zone}
Locality: {locality}
Site Name: {site_name}
Remark: {remark}
Date: {now}
"""
    filepath = "/tmp/info.txt"
    with open(filepath, "w") as f:
        f.write(content)

    file_drive = drive.CreateFile({'title': "info.txt", 'parents': [{'id': folder_id}]})
    file_drive.SetContentFile(filepath)
    file_drive.Upload()
    os.remove(filepath)

# Streamlit UI
st.title("Old Meter Photo Upload")

with st.form("upload_form", clear_on_submit=True):
    technician = st.text_input("Technician Name")
    zone = st.selectbox("Zone", ["NZ", "CZ", "SZ", "MCZ", "SCZ", "EZ"])
    locality = st.text_input("Locality")
    site_name = st.text_input("Site Name (Building)")
    remark = st.text_area("Remark (if any)")

    photo_files = st.file_uploader("Upload Old Meter Photos", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

    submitted = st.form_submit_button("Upload")

    if submitted:
        if technician and zone and locality and site_name and photo_files:
            building_folder_id = create_drive_folder(site_name, PARENT_FOLDER_ID)
            upload_metadata(building_folder_id, technician, zone, locality, site_name, remark)
            for photo in photo_files:
                upload_file_to_drive(photo, building_folder_id)

            st.success("All files and details uploaded successfully.")
        else:
            st.error("Please fill all fields and upload at least one photo.")
