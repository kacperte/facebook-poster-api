import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import datetime

SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
]
FILE_URL = "https://docs.google.com/spreadsheets/d/1L4FPum32xhQEm0NPovsIVLad-qqO0ozNdRpTbdgPWXU"
PATH = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "/var/secrets/google/key.json")
URL = os.environ.get("HOST_IP")
COLS_PER_DAY = 5
COL_OFFSET_TASK_STATUS = 5
FIRST_ROW = 3
LAST_ROW = 11


def reset_task_status():
    try:
        credentials = ServiceAccountCredentials.from_json_keyfile_name(PATH, SCOPE)
        client_gspread = gspread.authorize(credentials)
        spreadsheet = client_gspread.open_by_url(url=FILE_URL)
    except Exception as e:
        print(f"Problem z autoryzacją do arkusza kalkulacyjnego: {e}")
        return

    worksheet = spreadsheet.get_worksheet(2)

    current_day = datetime.datetime.today().weekday() - 1  # we have to change task status from previous day
    col_with_task_status = (current_day * COLS_PER_DAY) + COL_OFFSET_TASK_STATUS

    cells_to_update = []
    for row in range(FIRST_ROW, LAST_ROW):
        cell = worksheet.cell(row=row, col=col_with_task_status)
        cell.value = "FALSE"
        cells_to_update.append(cell)

    try:
        worksheet.update_cells(cells_to_update)
        print("Status zadań został zresetowany.")
    except Exception as e:
        print(f"Problem z aktualizacją komórek w arkuszu kalkulacyjnym: {e}")