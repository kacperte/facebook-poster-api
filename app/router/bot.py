from fastapi import APIRouter, Depends, HTTPException
from app.tasks import facebook_poster
import requests
import os
import json
from app.db import db_user, db_material, db_job_status
from app.db.database import get_db
from sqlalchemy.orm.session import Session
from app.config import SECRET_KEY_HASH
from app.db.hash import Hash
from pydantic import BaseModel, EmailStr, Field
import uuid
from ..schemas import JobStatusBase
from datetime import datetime


# Load the secret key hash from the app configuration
secret_key = SECRET_KEY_HASH

# Initialize the API router with the "/bot" prefix and "bot" tag
router = APIRouter(prefix="/bot", tags=["bot"])


# Define a Pydantic model for the content request data
class ContentRequest(BaseModel):
    login: str = Field(min_length=1, max_length=128)
    password: str = Field(min_length=1, max_length=128)
    email: EmailStr
    groups_name: str = Field(min_length=1, max_length=128)
    material_id: int = Field(gt=0, lt=1000)


@router.post(
    path="/run",
    summary="Run function that send content to Facebook groups",
    description="This API call function that send content to Facebook groups - text and image.",
)
def send_content_to_fb_groups(
    db: Session = Depends(get_db), content_request: ContentRequest = None
):
    with open("/tmp/adres-ip", "r") as file:
        ip = file.read().strip()

    URL = f"http://{ip}/"
    try:
        # Send a request to the token endpoint to authenticate the user
        response_token = requests.post(
            url=URL + "token",
            data={
                "grant_type": "password",
                "username": content_request.login,
                "password": content_request.password,
            },
        )
        response_token.raise_for_status()  # Raise an exception if the status code is not in the 200s
    except requests.HTTPError as e:
        # If an error occurs, raise an HTTPException with a 400 status code and an error message
        raise HTTPException(
            status_code=e.response.status_code, detail="Invalid credentials"
        )
    # Parse the access token from the token response and add it to the headers for subsequent requests
    response_dict = json.loads(response_token.content)
    auth_token = response_dict["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}

    try:
        # Send a request to the groups endpoint to retrieve a comma-separated list of group IDs
        response_groups = requests.get(
            url=URL + f"groups/group/{content_request.groups_name}",
            headers=headers,
        )
        response_dict = response_groups.json()
        groups = response_dict["groups"].split(",")
    except (ValueError, KeyError):
        # If an error occurs while parsing the response, raise an HTTPException with a 400 status code and an error
        # message
        raise HTTPException(status_code=400, detail="Invalid input")

    try:
        user = db_user.get_user(db, content_request.email)
    except Exception as e:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        material = db_material.get_material(db, content_request.material_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Material not found")

    try:
        # Attempt to retrieve the user from the database using the specified email address
        password = user.password
        enc_pass = Hash(secret_key).decrypt_password(password)
    except Exception as e:
        # If an error occurs while decrypting the password, raise an HTTPException with a 500 status code and an
        # error message
        raise HTTPException(status_code=500, detail="Error decrypting password")

    # Create unique string
    unique_string = str(uuid.uuid4())

    # Label groups with Label the groups with "non-processed"
    label_groups = {x: "non-processed" for x in groups}

    job_status_to_add = JobStatusBase(
        id=unique_string, date=datetime.now(), groups_to_procced=label_groups
    )
    db_job_status.create_job_status(db, job_status_to_add)

    # Use Celery to asynchronously send content to the specified Facebook groups
    task = facebook_poster.delay(
        login=content_request.email,
        password=enc_pass,
        image_name=material.image_name,
        text_name=material.text_name,
        id=unique_string,
    )
    return {"task_id": task.id}
