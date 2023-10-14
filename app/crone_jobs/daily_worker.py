import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
from urllib.parse import urljoin
import requests
import json
from kubernetes import client, config
import base64
import os


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
    """Make an API request and return the JSON response."""
    try:
        response = requests.request(method, url, headers=headers, **kwargs)
        response.raise_for_status()
        return json.loads(response.content)
    except requests.HTTPError as e:
        raise ValueError(
            f"Invalid credentials, HTTP status code: {e.response.status_code}"
        )


def get_secret_value(secret_name, namespace, key):
    config.load_incluster_config()
    v1 = client.CoreV1Api()

    secret = v1.read_namespaced_secret(secret_name, namespace)

    encoded_value = secret.data.get(key)
    if encoded_value:
        decoded_value = base64.b64decode(encoded_value).decode("utf-8")
        return decoded_value
    else:
        print(f"Klucz {key} nie został znaleziony w secret {secret_name}.")
        return None


def execute_daily_tasks():
    credentials = ServiceAccountCredentials.from_json_keyfile_name(PATH, SCOPE)
    client = gspread.authorize(credentials)
    spreadsheet = client.open_by_url(url=FILE_URL)
    worksheet = spreadsheet.get_worksheet(2)

    current_day = datetime.datetime.today().weekday()
    col_with_recruiter_login = (current_day * 5) + 2
    col_with_material_id = (current_day * 5) + 3
    col_with_groups_name = (current_day * 5) + 4
    col_with_task_status = (current_day * 5) + 5
    first_row = 3
    last_row = 11

    for row in range(first_row, last_row):
        if worksheet.cell(row, col_with_task_status).value == "FALSE":
            data = {
                "login": worksheet.cell(row, col_with_recruiter_login).value,
                "password": get_secret_value(
                    secret_name="crudentials-secrets",
                    namespace="default",
                    key=worksheet.cell(row, col_with_recruiter_login).value.split("@")[
                        0
                    ],
                ),
                "email": worksheet.cell(row, col_with_recruiter_login).value,
                "groups_name": worksheet.cell(row, col_with_groups_name).value,
                "material_id": int(worksheet.cell(row, col_with_material_id).value),
            }

            api_endpoint = urljoin(URL, "bot/run")
            response_dict = make_api_request(api_endpoint, method="POST", json=data)
            if response_dict:
                print(f"Zostało uruchomione nowe zadanie do wykonania.")
            else:
                return

            worksheet.update_cell(row=row, col=col_with_task_status, value="TRUE")

            return

execute_daily_tasks()