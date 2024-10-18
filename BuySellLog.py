import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime


def append_to_sheet(name, buy, sell, log_date=None):
    # Set up credentials (you'll need to set this up separately)
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file('./JSON/credentials.json', scopes=scopes)
    client = gspread.authorize(creds)

    # Open the Google Sheet (replace with your sheet ID)
    sheet = client.open_by_key('167ESbEe-uM_H6tb2LEaqnXAsqunI3MI6jLWcnNThxDU')

    # Check if the worksheet exists, if not create it
    try:
        worksheet = sheet.worksheet(name)
    except gspread.WorksheetNotFound:
        worksheet = sheet.add_worksheet(title=name, rows="100", cols="20")

    # Define column names
    column_names = ['Name', 'Buy', 'Sell', 'LogDate']

    # Check if column names exist, add them if they don't
    if worksheet.row_values(1) != column_names:
        worksheet.insert_row(column_names, 1)
        print(f"Added column names to sheet '{name}': {column_names}")

    # Use provided log_date or current date and time if not provided
    if log_date is None:
        log_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(log_date, datetime):
        log_date = log_date.strftime("%Y-%m-%d %H:%M:%S")

    # Prepare the data
    new_row = [name, buy, sell, log_date]

    # Append the new row
    worksheet.append_row(new_row)

    print(f"Data appended to sheet '{name}': {new_row}")


# Example usage
append_to_sheet("TATA", 100, 150)  # Uses current date and time
append_to_sheet("INFOSYS", 200, 250, datetime(2024, 9, 30, 15, 30, 0))  # Uses specified date and time
append_to_sheet("TATA", 110, 180)  # Uses current date and time
append_to_sheet("INFOSYS", 202, 302, datetime(2024, 9, 30, 15, 30, 0))  # Uses specified date and time