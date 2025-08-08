import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_sheet_data(sheet_name: str):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('app/credentials.json', scope)
    client = gspread.authorize(creds)

    sheet = client.open(sheet_name)
    worksheet = sheet.get_worksheet(0)  # First tab
    data = worksheet.get_all_records()  # List of dicts
    return data
