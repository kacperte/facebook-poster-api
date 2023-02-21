from fastapi import APIRouter, Depends, HTTPException
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
    try:
        response_token = requests.post(
            url="http://localhost:8000/token",
            data={
                "grant_type": "password",
                "username": content_request.login,
                "password": content_request.password,
            },
        )
        response_token.raise_for_status()
    except requests.HTTPError as e:
        raise HTTPException(status_code=e.response.status_code, detail="Invalid credentials")

    response_dict = json.loads(response_token.content)
    auth_token = response_dict["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}

    try:
        response_groups = requests.get(
            url=f"http://localhost:8000/gropus/group/{content_request.groups_name}",
            headers=headers,
        )
        response_dict = response_groups.json()
        groups = response_dict["groups"].split(",")
    except (ValueError, KeyError):
        raise HTTPException(status_code=400, detail="Invalid input")

    try:
        user = db_user.get_user(db, content_request.email)
    except Exception as e:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        password = user.password
        enc_pass = Hash(secret_key).decrypt_password(password)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error decrypting password")

    facebook_poster(login=content_request.email, password=enc_pass, groups=groups)