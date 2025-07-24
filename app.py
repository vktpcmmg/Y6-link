import streamlit as st
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
import tempfile

# ---------- CONFIGURATION ----------
GOOGLE_SHEET_NAME = "Meter Photo Uploads"
GOOGLE_DRIVE_FOLDER_ID = "13hG9ayDAHfK9MdVXUQwAYyZlUqWMKKYK"  # <-- CHANGE THIS

# ---------- AUTHENTICATION ----------
def authenticate_google_services():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)

    gauth = GoogleAuth()
    gauth.credentials = creds
    drive = GoogleDrive(gauth)

    return client, drive

# ---------- FILE UPLOAD ----------
def upload_file_to_drive(drive, file, filename):
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(file.read())
        tmp_file_path = tmp_file.name

    gfile = drive.CreateFile({'title': filename, 'parents': [{'id': GOOGLE_DRIVE_FOLDER_ID}]})
    gfile.SetContentFile(tmp_file_path)
    gfile.Upload()
    os.remove(tmp_file_path)
    return gfile['alternateLink']

# ---------- MAIN APP ----------
st.set_page_config(page_title="Meter Replacement Upload", layout="centered")

st.title("📸 Meter Replacement Entry Form")

with st.form("upload_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        technician = st.text_input("Technician Name*", max_chars=50)
        zone = st.selectbox("Zone*", ["NZ", "CZ", "SZ", "MCZ", "SCZ", "EZ"])
        locality = st.text_input("Locality*", max_chars=100)
    with col2:
        site_name = st.text_input("Site Name*", max_chars=100)
        remark = st.text_area("Remarks")

    st.markdown("---")
    st.subheader("🔢 Meter Numbers")

    col3, col4 = st.columns(2)
    with col3:
        old_meter_no = st.text_input("Old Meter Number*", max_chars=30)
        old_meter_photo = st.file_uploader("Old Meter Photo*", type=["jpg", "jpeg", "png"], key="old")
    with col4:
        new_meter_no = st.text_input("New Meter Number*", max_chars=30)
        new_meter_photo = st.file_uploader("New Meter Photo*", type=["jpg", "jpeg", "png"], key="new")

    submitted = st.form_submit_button("Submit")

    if submitted:
        if not all([technician, zone, locality, site_name, old_meter_no, new_meter_no, old_meter_photo, new_meter_photo]):
            st.error("❌ Please fill all required fields and upload both photos.")
        else:
            with st.spinner("Uploading to Google Drive & Sheets..."):
                client, drive = authenticate_google_services()
                sheet = client.open(GOOGLE_SHEET_NAME).sheet1

                # Upload files
                old_photo_link = upload_file_to_drive(drive, old_meter_photo, f"{old_meter_no}_OLD.jpg")
                new_photo_link = upload_file_to_drive(drive, new_meter_photo, f"{new_meter_no}_NEW.jpg")

                # Add row to Google Sheet
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sheet.append_row([
                    now,
                    technician,
                    zone,
                    locality,
                    site_name,
                    old_meter_no,
                    old_photo_link,
                    new_meter_no,
                    new_photo_link,
                    remark
                ])

                st.success("✅ Submission Successful!")

# ---------- Footer ----------
st.markdown("---")
st.caption("Developed for meter replacement task logging — Vinay 2025")
