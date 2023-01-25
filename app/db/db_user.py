from sqlalchemy.orm.session import Session
from app.schemas import UserBase
from app.db.models import DbUser
from fastapi import HTTPException, status
from app.db.hash import Hash


def create_user(db: Session, request: UserBase):
    """
    Create new user
    """
    new_user = DbUser(
        username=request.username,
        email=request.email,
        password=Hash.encrypt_password(request.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def get_all_users(db: Session):
    """
    Get all users
    """
    return db.query(DbUser).all()


def get_user(db: Session, mail: str):
    """
    Get one user by email
    """
    user = db.query(DbUser).filter(DbUser.email == mail).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {mail} not found",
        )
    return user


def get_user_by_name(db: Session, username: str):
    """
    Get one user by username. Must for authentication.
    """
    user = db.query(DbUser).filter(DbUser.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {username} not found",
        )
    return user


def update_user(db: Session, id: str, request: UserBase):
    """
    Update one  user
    """
    user = db.query(DbUser).filter(DbUser.email == id)
    if not user.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {id} not found",
        )
    user.update(
        {
            DbUser.username: request.username,
            DbUser.email: request.email,
            DbUser.password: Hash.encrypt_password(request.password),
        }
    )
    db.commit()
    return "ok"


def delete_user(db: Session, id: str):
    """
    Delete one  user
    """
    user = db.query(DbUser).filter(DbUser.email == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {id} not found",
        )
    db.delete(user)
    db.commit()
    return "ok"
