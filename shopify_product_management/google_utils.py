import io
import logging
import os
import re
import gspread
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from PIL import Image

logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)

google_credentials = None
def authenticate_google_api(google_credential_path):
    # Authenticate to Google API using Service Account
    global google_credentials
    if not google_credentials:
        google_credentials = Credentials.from_service_account_file(
            google_credential_path,
            scopes=['https://www.googleapis.com/auth/drive',
                    'https://www.googleapis.com/auth/spreadsheets']
        )
    return google_credentials


_gdrive_service = None
def gdrive_service(google_credential_path):
    global _gdrive_service
    if not _gdrive_service:
        _gdrive_service = build('drive', 'v3', credentials=authenticate_google_api(google_credential_path))
    return _gdrive_service


def gspread_access(google_credential_path):
    creds = authenticate_google_api(google_credential_path)
    return gspread.authorize(creds)


def natural_compare(k):
    def convert(text):
        return int(text) if text.isdigit() else text.lower()

    return [convert(c) for c in re.split('([0-9]+)', k)]


def get_drive_image_details(google_credential_path, folder_id, sku, image_prefix):
    service = gdrive_service(google_credential_path)
    results = service.files().list(
                        q=f"'{folder_id}' in parents",
                        pageSize=1000,
                        includeItemsFromAllDrives=True,
                        supportsAllDrives=True,
                    ).execute()
    items = results.get('files', [])

    # Sort files using natural order
    items.sort(key=lambda f: natural_compare(f['name']))

    res = []
    sequence = 0

    for sequence, item in enumerate(items):
        if item['mimeType'].startswith('image/'):
            file_metadata = {
                'name': f"{image_prefix}_{sku}_{str(sequence).zfill(2)}_{item['name']}",
                'mimeType': item['mimeType'],
                'id': item['id'],
                # 'downloadUrl': f"https://www.googleapis.com/drive/v3/files/{item['id']}?alt=media"
            }
            res.append(file_metadata)
    return res

def resize_image_to_limit(image_path, output_path, max_megapixels=20):
    with Image.open(image_path) as img:
        # Calculate current image size in megapixels
        current_megapixels = (img.width * img.height) / 1_000_000

        # Check if resizing is necessary
        if current_megapixels > max_megapixels:
            scale_factor = (max_megapixels / current_megapixels) ** 0.5
            new_width = int(img.width * scale_factor)
            new_height = int(img.height * scale_factor)

            # Resize the image with LANCZOS filter
            resized_img = img.resize((new_width, new_height), Image.LANCZOS)
            if resized_img.mode == 'RGBA':
                kwargs = dict(format='PNG')
            else:
                kwargs = dict(format='JPEG', quarity=85)
            resized_img.save(output_path, **kwargs)
            logger.info(f"Image resized to {new_width}x{new_height} pixels and saved as {kwargs}")


def download_images_from_drive(google_credential_path, drive_image_details, local_dir):
    res = []
    for file_details in drive_image_details:
        if not os.path.exists(local_dir):
            os.mkdir(local_dir)
        local_path = os.path.join(local_dir, file_details['name'])
        if not os.path.exists(local_path):
            logger.info(f"  starting download of {file_details['name']}")
            download_file_from_drive(google_credential_path, file_details['id'], local_path)
            resize_image_to_limit(local_path, local_path)
        res.append(local_path)
    return res


def download_file_from_drive(google_credential_path, file_id, destination_path):
    service = gdrive_service(google_credential_path)
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(destination_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        logger.debug(f"Download {int(status.progress() * 100)}%.")


def get_sheet_index_by_title(google_credential_path, sheet_id, sheet_title):
    worksheet = gspread_access(google_credential_path).open_by_key(sheet_id)
    for meta in worksheet.fetch_sheet_metadata()['sheets']:
        if meta['properties']['title'] == sheet_title:
            return meta['properties']['index']
    raise RuntimeError(f'Did not find a sheet named {sheet_title}')


def get_link(google_credential_path, spreadsheet_id, sheet_title, row, row_num, column_num):
    link = row[column_num]
    if all([link, link != 'no image', not link.startswith('http')]):
        link = get_richtext_link(google_credential_path, spreadsheet_id, sheet_title, row_num, column_num)
    return link


def get_richtext_link(google_credential_path, spreadsheet_id, sheet_title, row, column):
    # Use the Google Sheets API directly for rich text data
    from googleapiclient.discovery import build
    service = build("sheets", "v4", credentials=authenticate_google_api(google_credential_path))
    import string
    range_notation = f'{sheet_title}!{string.ascii_uppercase[column]}{row}'
    response = service.spreadsheets().get(
        spreadsheetId=spreadsheet_id,
        ranges=range_notation,
        fields="sheets(data(rowData(values)))"
    ).execute()
    hyperlink = (
        response.get("sheets", [])[0]
        .get("data", [])[0]
        .get("rowData", [])[0]
        .get("values", [])[0]
        .get("hyperlink")
    )
    print(f"The hyperlink is: {hyperlink}")
    return hyperlink


def drive_link_to_id(link):
    return (link.rsplit('/', 1)[-1].replace('open?id=', '')
                                   .replace('?usp=drive_link', '')
                                   .replace('?usp=sharing', '')
                                   .replace('&usp=drive_fs', '')
                                   .replace('?dmr=1&ec=wgc-drive-globalnav-goto', ''))


def worksheet_rows(google_credential_path, sheet_id, sheet_title):
    sheet_index = get_sheet_index_by_title(google_credential_path, sheet_id, sheet_title)
    worksheet = gspread_access(google_credential_path).open_by_key(sheet_id).get_worksheet(sheet_index)
    return worksheet.get_all_values()
