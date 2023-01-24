from fastapi import APIRouter, Depends
from app.schemas import UserBase, UserDisplay
from sqlalchemy.orm.session import Session
from app.db.database import get_db
from app.db import db_user
from typing import List
from app.auth.oauth2 import get_current_user

router = APIRouter(prefix="/user", tags=["user"])


@router.post(
    path="/",
    summary="Create new user",
    description="This API call function that create new user.",
    response_model=UserDisplay,
)
def create_user(
    request: UserBase,
    db: Session = Depends(get_db),
    #  current_user: UserBase = Depends(get_current_user),
):
    """
    Create new user
    """
    return db_user.create_user(db, request)


@router.get(
    path="/",
    summary="Read all users",
    description="This API call function t hat read all users.",
    response_model=List[UserDisplay],
)
def get_all_users(
    db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_user)
):
    """
    Get all users
    """
    return db_user.get_all_users(db)


@router.get(
    path="/{email}",
    summary="Read one user by email",
    description="This API call function that read one user.",
    response_model=UserDisplay,
)
def get_one_user(
    email: str,
    db: Session = Depends(get_db),
    current_user: UserBase = Depends(get_current_user),
):
    """
    Get one user by email
    """
    return db_user.get_user(db, email)


@router.put(
    path="/{email}",
    summary="Update user",
    description="This API call function that update user.",
)
def update_user(
    email: str,
    request: UserBase,
    db: Session = Depends(get_db),
    current_user: UserBase = Depends(get_current_user),
):
    return db_user.update_user(db, email, request)


@router.delete(
    path="/delete/{mail}",
    summary="Delete user",
    description="This API call function that delete user.",
)
def delete_user(
    mail: str,
    db: Session = Depends(get_db),
    current_user: UserBase = Depends(get_current_user),
):
    """
    Delete user
    """
    return db_user.delete_user(db, mail)
