from google.cloud import storage
import os
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.schemas import MaterialBase, MaterialDisplay, UserBase
from sqlalchemy.orm.session import Session
from app.db.database import get_db
from app.db import db_material, db_user
from typing import List, Tuple
from tempfile import NamedTemporaryFile
from app.auth.oauth2 import get_current_user

router = APIRouter(prefix="/material", tags=["material"])

# Initialize a storage client
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/var/secrets/google/key.json"
storage_client = storage.Client()


def get_file_extension(file: UploadFile) -> Tuple[str, str]:
    filename, file_extension = os.path.splitext(file.filename)
    file_extension = file_extension.lstrip(".")
    return filename, file_extension


def upload_file_to_gcp_storage_fastapi(
    bucket_name: str,
    client_name: str,
    position_name: str,
    type_of_file: str,
    file: UploadFile = File(...),
):
    """
    Upload file to GCP Storage
    """
    if not isinstance(bucket_name, str):
        raise ValueError("Invalid value for argument 'bucket_name'. Expected string.")
    if not isinstance(client_name, str):
        raise ValueError("Invalid value for argument 'client_name'. Expected string.")
    if not isinstance(position_name, str):
        raise ValueError("Invalid value for argument 'position_name'. Expected string.")
    if type_of_file not in ["content", "copy"]:
        raise ValueError(
            "Invalid value for argument 'type_of_file'. Expected 'content' or 'copy'."
        )
    if not file.file:
        raise HTTPException(status_code=400, detail="File is empty")

    # Get file extension
    filename, file_extension = get_file_extension(file)

    # Prepare file path name
    upload_path = f"{type_of_file}/{client_name.lower()}__{position_name.lower()}.{file_extension}"
    print(upload_path, bucket_name)
    # handle upload object
    temp = NamedTemporaryFile(delete=False)
    try:
        contents = file.file.read()
        with temp as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"There was an error uploading the file - {e}"
        )
    finally:
        file.file.close()

    # get bucket with name
    bucket = storage_client.get_bucket(bucket_name)

    # check if blob already exists
    blob = bucket.blob(upload_path)
    if blob.exists():
        raise HTTPException(
            status_code=400,
            detail="File with the same name already exists in the bucket.",
        )

    # upload to GCS
    try:
        blob.upload_from_filename(temp.name)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"There was an error uploading the file - {e}"
        )
    return upload_path


@router.post(
    path="/",
    summary="Create new material",
    description="This API call function that create new material.",
    response_model=MaterialDisplay,
)
async def create_material(
    client: str,
    position: str,
    db: Session = Depends(get_db),
    image: UploadFile = File(...),
    text_content: UploadFile = File(...),
    current_user: UserBase = Depends(get_current_user),
):
    user = db_user.get_user_by_name(db=db, username=current_user.email).id
    newMaterial = MaterialBase(
        client=client.lower(),
        position=position.lower(),
        image_name=upload_file_to_gcp_storage_fastapi(
            bucket_name="fb-poster-storage",
            client_name=client,
            position_name=position,
            type_of_file="content",
            file=image,
        ),
        text_name=upload_file_to_gcp_storage_fastapi(
            bucket_name="fb-poster-storage",
            client_name=client,
            position_name=position,
            type_of_file="copy",
            file=text_content,
        ),
        creator_id=user,
    )

    new_material = db_material.create_material(db, newMaterial)
    if not new_material.id:
        raise HTTPException(status_code=400, detail="Failed to create new material")

    return new_material


@router.get(
    path="/",
    summary="Read all materials",
    description="This API call function that read all materials.",
    response_model=List[MaterialDisplay],
)
async def get_all_materials(
    db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_user)
):
    return db_material.get_all_materials(db)


@router.get(
    path="/{id}",
    summary="Read one material by id",
    description="This API call function that read one material.",
    response_model=MaterialDisplay,
)
async def get_one_materials(
    id: int,
    db: Session = Depends(get_db),
    current_user: UserBase = Depends(get_current_user),
):
    return db_material.get_material(db, id)


@router.get(
    path="/client/{client}",
    summary="Read one material by client name",
    description="This API call function that read one material.",
    response_model=List[MaterialDisplay],
)
async def get_materials_by_client(
    client: str,
    db: Session = Depends(get_db),
    current_user: UserBase = Depends(get_current_user),
):
    return db_material.get_all_materials_by_client(db, client.lower())


@router.put(
    path="/{id}",
    summary="Update material",
    description="This API call function that update material.",
)
async def update_material(
    id: int,
    client: str,
    position: str,
    image: UploadFile = File(...),
    text_content: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserBase = Depends(get_current_user),
):
    user_id = db_user.get_user_by_name(db=db, username=current_user.username).id

    newMaterial = MaterialBase(
        client=client.lower(),
        position=position.lower(),
        image_name=upload_file_to_gcp_storage_fastapi(
            bucket_name="fb-poster-storage",
            client_name=client,
            position_name=position,
            type_of_file="content",
            file=image,
        ),
        text_name=upload_file_to_gcp_storage_fastapi(
            bucket_name="fb-poster-storage",
            client_name=client.lower(),
            position_name=position.lower(),
            type_of_file="copy",
            file=text_content,
        ),
        creator_id=user_id,
    )

    return db_material.update_material(db, id, newMaterial)


@router.delete(
    path="/delete/{id}",
    summary="Delete material",
    description="This API call function that delete material.",
)
async def delete_user(
    id: int,
    db: Session = Depends(get_db),
    current_user: UserBase = Depends(get_current_user),
):
    deleted_material = db_material.delete_material(db, id)
    if not deleted_material:
        raise HTTPException(status_code=404, detail="Material not found")

    return deleted_material
