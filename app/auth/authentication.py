from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm.session import Session
from app.db.database import get_db
from app.db import models
from app.db.hash import Hash
from app.auth.oauth2 import create_access_token
from app.config import SECRET_KEY_HASH

secret_key = SECRET_KEY_HASH

router = APIRouter(tags=["authentication"])


@router.post("/token")
def get_token(
        request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = (
        db.query(models.DbUser)
        .filter(models.DbUser.username == request.username)
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentails"
        )

    if not Hash(secret_key).verify_password(
            hashed_password=user.password, plain_password=request.password
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Incorrect password"
        )

    access_token = create_access_token(data={"sub": user.username})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
    }
