import csv
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.schemas import GroupsBase, GroupsDispaly, UserBase
from typing import List
from sqlalchemy.orm.session import Session
from app.db.database import get_db
from app.db import db_groups
from tempfile import NamedTemporaryFile
from app.auth.oauth2 import get_current_user


router = APIRouter(prefix="/gropus", tags=["gropus"])


def process_csv_file(file):
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

    # get texts from csv and proces it to one str
    try:
        with open(temp.name, "r") as file:
            reader = csv.reader(file, delimiter=",")
            str_to_save = ",".join([row[0] for row in reader])
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"There was an error reading the CSV file - {e}"
        )
    return str_to_save


@router.post(
    path="/",
    summary="Create new FB group list",
    description="This API call function that create new FB group list.",
    response_model=GroupsDispaly,
)
def create_group(
    groups_name: str,
    groups: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserBase = Depends(get_current_user),
):
    newGroup = GroupsBase(
        groups_name=groups_name,
        groups=process_csv_file(groups),
    )
    groups = db_groups.create_gropus(db, newGroup)
    if not groups.id:
        raise HTTPException(status_code=400, detail="Error creating groups.")
    return groups


@router.get(
    path="/",
    summary="Read all groups",
    description="This API call function that read all FB groups.",
    response_model=List[GroupsDispaly],
)
def get_all_groups(
    db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_user)
):
    return db_groups.get_all_groups(db)


@router.get(
    path="/group/{groups_name}",
    summary="Read one material by group name",
    description="This API call function that read FB group by group name.",
    response_model=GroupsDispaly,
)
def get_group_by_name(
    groups_name: str,
    db: Session = Depends(get_db),
    current_user: UserBase = Depends(get_current_user),
):
    return db_groups.get_group_by_group_name(db, groups_name)


@router.put(
    path="/group/{id}",
    summary="Update group",
    description="This API call function that update FB group.",
)
def update_group(
    id: int,
    groups_name: str,
    groups: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserBase = Depends(get_current_user),
):
    newGroup = GroupsBase(
        groups_name=groups_name,
        groups=process_csv_file(groups),
    )

    return db_groups.update_groups(db, request=newGroup, id=id)


@router.delete(
    path="/delete/{groups_name}",
    summary="Delete group",
    description="This API call function that delete group.",
)
def delete_group(
    groups_name: str,
    db: Session = Depends(get_db),
    current_user: UserBase = Depends(get_current_user),
):
    return db_groups.delete_groups(db, groups_name)
