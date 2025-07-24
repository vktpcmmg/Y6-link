import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from datetime import datetime

# === CONFIG ===
FOLDER_ID = "13hG9ayDAHfK9MdVXUQwAYyZlUqWMKKYK"  # Replace with actual folder ID

# === Google Auth ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
gc = gspread.authorize(creds)
gauth = GoogleAuth()
gauth.credentials = creds
drive = GoogleDrive(gauth)

# === Google Sheet ===
sheet = gc.open("Meter Photo Uploads").sheet1

# === Streamlit UI ===
st.title("📷 Meter Replacement Upload")

with st.form("upload_form", clear_on_submit=True):
    technician = st.text_input("Technician Name")
    zone = st.selectbox("Zone", ["NZ", "CZ", "SZ", "MCZ", "SCZ", "EZ"])
    locality = st.text_input("Locality")
    site_name = st.text_input("Site Name")
    remark = st.text_input("Remark")

    old_photo = st.file_uploader("Upload OLD Meter Photo", type=["jpg", "jpeg", "png"])
    new_photo = st.file_uploader("Upload NEW Meter Photo", type=["jpg", "jpeg", "png"])

    submitted = st.form_submit_button("Submit")

if submitted:
    if technician and old_photo and new_photo:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Upload OLD Photo
        old_file = drive.CreateFile({'title': f"{technician}_OLD_{timestamp}.jpg", 'parents': [{'id': FOLDER_ID}]})
        old_file.SetContentFile(old_photo.name)
        old_file.Upload()
        old_file['shared'] = True
        old_file.Upload()
        old_link = old_file['alternateLink']

        # Upload NEW Photo
        new_file = drive.CreateFile({'title': f"{technician}_NEW_{timestamp}.jpg", 'parents': [{'id': FOLDER_ID}]})
        new_file.SetContentFile(new_photo.name)
        new_file.Upload()
        new_file['shared'] = True
        new_file.Upload()
        new_link = new_file['alternateLink']

        # Save to Google Sheet
        sheet.append_row([
            timestamp, technician, zone, locality, site_name, remark, old_link, new_link
        ])
        st.success("✅ Submitted successfully!")
        st.markdown(f"[📷 View OLD Photo]({old_link})")
        st.markdown(f"[📷 View NEW Photo]({new_link})")
    else:
        st.warning("Please fill all fields and upload both photos.")
