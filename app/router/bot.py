from fastapi import APIRouter, Depends
from app.tasks import facebook_poster
import requests
import json
from app.db import db_user
from app.db.database import get_db
from sqlalchemy.orm.session import Session
from app.config import SECRET_KEY_HASH
from app.db.hash import Hash
from pydantic import BaseModel


secret_key = SECRET_KEY_HASH


router = APIRouter(prefix="/bot", tags=["bot"])


class ContentRequest(BaseModel):
    login: str
    password: str
    email: str
    groups_name: str


@router.post(
    path="/run",
    summary="Run function that send content to Facebook groups",
    description="This API call function that send content to Facebook groups - text and image.",
)
def send_content_to_fb_groups(
    db: Session = Depends(get_db), content_request: ContentRequest = None
):

    response_token = requests.post(
        url="http://localhost:8000/token",
        data={
            "grant_type": "password",
            "username": content_request.login,
            "password": content_request.password,
        },
    ).content
    response_dict = json.loads(response_token)
    auth_token = response_dict["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}

    response_groups = requests.get(
        url=f"http://localhost:8000/gropus/group/{content_request.groups_name}",
        headers=headers,
    ).content
    response_dict = json.loads(response_groups)
    groups = response_dict["groups"].split(",")

    password = db_user.get_user(db, content_request.email).password
    enc_pass = Hash(secret_key).decrypt_password(password)

    facebook_poster(login=content_request.email, password=enc_pass, groups=groups)