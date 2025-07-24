import streamlit as st
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import tempfile
import os
import json

# --- Authenticate with Google Drive using secrets ---
def gdrive_login():
    gauth = GoogleAuth()

    # Use secrets from Streamlit
    gauth.credentials = gauth.LoadServiceConfigSettings()
    gauth.ServiceAuth()
    return GoogleDrive(gauth)

# --- Upload files to Drive folder named after Building Name ---
def upload_photos(drive, building_name, images, parent_folder_id):
    # Check if building folder already exists
    file_list = drive.ListFile({'q': f"'{parent_folder_id}' in parents and trashed=false"}).GetList()
    folder_id = None
    for file in file_list:
        if file['title'] == building_name and file['mimeType'] == 'application/vnd.google-apps.folder':
            folder_id = file['id']
            break

    # If not exists, create new folder
    if not folder_id:
        folder_metadata = {
            'title': building_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [{'id': parent_folder_id}]
        }
        folder = drive.CreateFile(folder_metadata)
        folder.Upload()
        folder_id = folder['id']

    # Upload each image to the folder
    for image in images:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(image.read())
            tmp_file_path = tmp_file.name

        file_drive = drive.CreateFile({'title': image.name, 'parents': [{'id': folder_id}]})
        file_drive.SetContentFile(tmp_file_path)
        file_drive.Upload()
        os.remove(tmp_file_path)

# --- Streamlit UI ---
st.title("Meter Photo Upload App")

with st.form("upload_form"):
    technician_name = st.text_input("Technician Name")
    locality = st.text_input("Locality")
    building_name = st.text_input("Building Name")
    remark = st.text_area("Remark")
    uploaded_images = st.file_uploader("Upload Meter Photos", accept_multiple_files=True, type=['jpg', 'jpeg', 'png'])

    submitted = st.form_submit_button("Upload")

if submitted:
    if technician_name and locality and building_name and uploaded_images:
        # Build credentials from st.secrets
        credentials_dict = dict(st.secrets["gdrive"])
        credentials_dict["private_key"] = credentials_dict["private_key"].replace("\\n", "\n")

        with open("service_account.json", "w") as f:
            json.dump(credentials_dict, f)

        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "service_account.json"

        # Login and upload
        drive = gdrive_login()
        PARENT_FOLDER_ID = "13hG9ayDAHfK9MdVXUQwAYyZlUqWMKKYK"  # 🔁 Replace with your Drive folder ID
        upload_photos(drive, building_name, uploaded_images, PARENT_FOLDER_ID)

        st.success(f"Uploaded to folder: {building_name}")
    else:
        st.error("Please fill all fields and upload at least one photo.")
