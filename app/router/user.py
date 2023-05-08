from fastapi import APIRouter, Depends, HTTPException
from app.schemas import UserBase, UserDisplay
from sqlalchemy.orm.session import Session
from app.db.database import get_db
from app.db import db_user
from typing import List
from app.auth.oauth2 import get_current_user
from pydantic import EmailStr


router = APIRouter(prefix="/user", tags=["user"])


@router.post(
    path="/",
    summary="Create new user",
    description="This API call function that create new user.",
    response_model=UserDisplay,
)
async def create_user(
    request: UserBase,
    db: Session = Depends(get_db),
    # current_user: UserBase = Depends(get_current_user),
):
    if db_user.get_user_by_name(db, request.username):
        raise HTTPException(status_code=409, detail="Username already in database")

    user = db_user.create_user(db, request)

    if not user.id:
        raise HTTPException(status_code=400, detail="Error creating user.")

    return user


@router.get(
    path="/",
    summary="Read all users",
    description="This API call function t hat read all users.",
    response_model=List[UserDisplay],
)
async def get_all_users(
    db: Session = Depends(get_db), current_user: UserBase = Depends(get_current_user)
):
    return db_user.get_all_users(db)


@router.get(
    path="/{email}",
    summary="Read one user by email",
    description="This API call function that read one user.",
    response_model=UserDisplay,
)
async def get_one_user(
    email: str = EmailStr,
    db: Session = Depends(get_db),
    current_user: UserBase = Depends(get_current_user),
):
    return db_user.get_user(db, email)


@router.put(
    path="/{email}",
    summary="Update user",
    description="This API call function that update user.",
)
async def update_user(
    email: str = EmailStr,
    request: UserBase = None,
    db: Session = Depends(get_db),
    current_user: UserBase = Depends(get_current_user),
):
    return db_user.update_user(db, email, request)


@router.delete(
    path="/delete/{mail}",
    summary="Delete user",
    description="This API call function that delete user.",
)
async def delete_user(
    mail: str = EmailStr,
    db: Session = Depends(get_db),
    current_user: UserBase = Depends(get_current_user),
):

    return db_user.delete_user(db, mail)
