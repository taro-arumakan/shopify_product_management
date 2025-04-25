import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from helpers.google_api_interface.drive import GoogleDriveApiInterface
from helpers.google_api_interface.sheets import GoogleSheetsApiInterface

class GoogleApiInterface(GoogleDriveApiInterface, GoogleSheetsApiInterface):
    def __init__(self, google_credential_path, sheet_id=None):
        self.google_credential_path = google_credential_path
        self.scopes = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
        self.credentials = Credentials.from_service_account_file(self.google_credential_path, scopes=self.scopes)
        self.drive_service = build('drive', 'v3', credentials=self.credentials)
        self.sheets_service = build('sheets', 'v4', credentials=self.credentials)
        self.gspread_client = gspread.authorize(self.credentials)
        self.sheet_id = sheet_id
