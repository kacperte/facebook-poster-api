import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
from urllib.parse import urljoin
import requests
import json
from kubernetes import client, config
import base64
import os
from app.agents.logger import create_logger

logger = create_logger(__name__)


COLS_PER_DAY = 5
COL_OFFSET_RECRUITER = 2
COL_OFFSET_MATERIAL_ID = 3
COL_OFFSET_GROUPS_NAME = 4
COL_OFFSET_TASK_STATUS = 5
FIRST_ROW = 3
LAST_ROW = 11

SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
]
FILE_URL = "https://docs.google.com/spreadsheets/d/1L4FPum32xhQEm0NPovsIVLad-qqO0ozNdRpTbdgPWXU"
PATH = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "/var/secrets/google/key.json")
URL = os.environ.get("HOST_IP")


def make_api_request(url, headers=None, method="GET", **kwargs):
    try:
        response = requests.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()

        if not response.content:
            raise ValueError("Empty response from API")

        return json.loads(response.content)
    except requests.HTTPError as e:
        raise ValueError(f"HTTP status code: {e.response.status_code}")


def get_secret_value(secret_name, namespace, key):
    config.load_incluster_config()
    v1 = client.CoreV1Api()

    secret = v1.read_namespaced_secret(secret_name, namespace)
    encoded_value = secret.data.get(key)
    if encoded_value:
        decoded_value = base64.b64decode(encoded_value).decode("utf-8")
        return decoded_value
    else:
        logger.error(f"Klucz {key} nie został znaleziony w secret {secret_name}.")
        return None


def execute_daily_tasks():
    try:
        credentials = ServiceAccountCredentials.from_json_keyfile_name(PATH, SCOPE)
        client_gspread = gspread.authorize(credentials)
        spreadsheet = client_gspread.open_by_url(url=FILE_URL)
    except Exception as e:
        logger.error(f"Problem z autoryzacją do arkusza kalkulacyjnego: {e}")
        return

    worksheet = spreadsheet.get_worksheet(2)

    current_day = datetime.datetime.today().weekday()
    col_with_recruiter_login = (current_day * COLS_PER_DAY) + COL_OFFSET_RECRUITER
    col_with_material_id = (current_day * COLS_PER_DAY) + COL_OFFSET_MATERIAL_ID
    col_with_groups_name = (current_day * COLS_PER_DAY) + COL_OFFSET_GROUPS_NAME
    col_with_task_status = (current_day * COLS_PER_DAY) + COL_OFFSET_TASK_STATUS

    for row in range(FIRST_ROW, LAST_ROW):
        if (worksheet.cell(row, col_with_task_status).value == "FALSE" and
                worksheet.cell(row, col_with_recruiter_login).value):
            data = {
                "login": worksheet.cell(row, col_with_recruiter_login).value,
                "password": get_secret_value(
                    secret_name="crudentials-secrets",
                    namespace="default",
                    key=worksheet.cell(row, col_with_recruiter_login).value.split("@")[0],
                ),
                "email": worksheet.cell(row, col_with_recruiter_login).value,
                "groups_name": worksheet.cell(row, col_with_groups_name).value,
                "material_id": int(worksheet.cell(row, col_with_material_id).value),
            }

            api_endpoint = urljoin(URL, "bot/run")
            try:
                response_dict = make_api_request(api_endpoint, method="POST", json=data)
                if response_dict:
                    logger.info(f"Zostało uruchomione nowe zadanie do wykonania.")
            except ValueError as e:
                logger.error(f"Błąd podczas żądania API: {e}")

            worksheet.update_cell(row=row, col=col_with_task_status, value="TRUE")


if __name__ == "__main__":
    execute_daily_tasks()
