import boto3
import os
from fastapi import APIRouter, Depends, UploadFile, File
from app.schemas import MaterialBase, MaterialDisplay
from sqlalchemy.orm.session import Session
from app.db.database import get_db
from app.db import db_material
from typing import List
from tempfile import NamedTemporaryFile


router = APIRouter(prefix="/material", tags=["material"])


def upload_file_to_s3_fastapi(bucket, file, client, position, type_of_file):

    # prepre file path name
    upload_path = f"{type_of_file}/{client}__{position}"

    # add proper file extension
    if type_of_file == "content":
        upload_path += ".txt"
    else:
        upload_path += ".jpg"

    # handle upload object
    temp = NamedTemporaryFile(delete=False)
    try:
        contents = file.file.read()
        with temp as f:
            f.write(contents);
    except Exception as e:
        return {"message": f"There was an error uploading the file - {e}"}
    finally:
        file.file.close()

    # upload to s3 section
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv('ACCESS_KEY'),
        aws_secret_access_key=os.getenv('SECRET_KEY'),
    )
    with open(temp.name, "rb") as data:
        s3.upload_fileobj(data, bucket, upload_path)

    return upload_path


@router.post(
    path="/",
    summary="Create new material",
    description="This API call function that create new material.",
    response_model=MaterialDisplay,
)
def create_material(
    client: str,
    position: str,
    creator_id: int,
    db: Session = Depends(get_db),
    image: UploadFile = File(...),
    text_content: UploadFile = File(...),
):
    newMaterial = MaterialBase(
        client=client,
        position=position,
        image=upload_file_to_s3_fastapi(
            bucket="heroku-fb-poster",
            client=client,
            position=position,
            type_of_file="content",
            file=image,
        ),
        text=upload_file_to_s3_fastapi(
            bucket="heroku-fb-poster",
            client=client,
            position=position,
            type_of_file="copy",
            file=text_content,
        ),
        creator_id=creator_id,
    )
    return db_material.create_material(db, newMaterial)


@router.get(
    path="/",
    summary="Read all materials",
    description="This API call function that read all materials.",
    response_model=List[MaterialDisplay],
)
def get_all_materials(db: Session = Depends(get_db)):
    return db_material.get_all_materials(db)


@router.get(
    path="/{id}",
    summary="Read one material by id",
    description="This API call function that read one material.",
    response_model=MaterialDisplay,
)
def get_one_materials(id: int, db: Session = Depends(get_db)):
    return db_material.get_material(db, id)


@router.get(
    path="/client/{client}",
    summary="Read one material by client name",
    description="This API call function that read one material.",
    response_model=List[MaterialDisplay]
)
def get_materials_by_client(client: str, db: Session = Depends(get_db)):
    return db_material.get_all_materials_by_client(db, client)


@router.put(
    path="/{id}",
    summary="Update material",
    description="This API call function that update material.",
)
def update_material(
        id: int,
        client: str,
        position: str,
        creator_id: int,
        image: UploadFile = File(...),
        text_content: UploadFile = File(...),
        db: Session = Depends(get_db)):
    newMaterial = MaterialBase(
        client=client,
        position=position,
        image=upload_file_to_s3_fastapi(
            bucket="heroku-fb-poster",
            client=client,
            position=position,
            type_of_file="content",
            file=image,
        ),
        text=upload_file_to_s3_fastapi(
            bucket="heroku-fb-poster",
            client=client,
            position=position,
            type_of_file="copy",
            file=text_content,
        ),
        creator_id=creator_id,
    )
    return db_material.update_material(db, id, newMaterial)


@router.delete(
    path="/delete/{id}",
    summary="Delete material",
    description="This API call function that delete material.",
)
def delete_user(
    id: int,
    db: Session = Depends(get_db),
):
    return db_material.delete_material(db, id)

