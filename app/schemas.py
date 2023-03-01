from pydantic import BaseModel, Field, EmailStr, ConstrainedList
from typing import List


class Material(BaseModel):
    client: str = Field(min_length=1, max_length=128)
    position: str = Field(min_length=1, max_length=128)
    image_name: str = Field(min_length=1, max_length=128)
    text_name: str = Field(min_length=1, max_length=128)

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=128)
    email: str = EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserDisplay(BaseModel):
    id: int = Field(max_digits=3)
    username: str = Field(min_length=1, max_length=128)
    email: str = EmailStr
    items: List[Material] = []

    class Config:
        orm_mode = True


class User(BaseModel):
    id: int = Field(max_digits=3)
    username: str = Field(min_length=1, max_length=128)

    class Config:
        orm_mode = True


class MaterialBase(BaseModel):
    client: str = Field(min_length=1, max_length=128)
    position: str = Field(min_length=1, max_length=128)
    image_name: str = Field(min_length=1, max_length=128)
    text_name: str = Field(min_length=1, max_length=128)
    creator_id: int = Field(max_digits=3)


class MaterialDisplay(BaseModel):
    id: int = Field(max_digits=3)
    client: str = Field(min_length=1, max_length=128)
    position: str = Field(min_length=1, max_length=128)
    image_name: str = Field(min_length=1, max_length=128)
    text_name: str = Field(min_length=1, max_length=128)
    user: User

    class Config:
        orm_mode = True


class GroupsBase(BaseModel):
    groups_name: str = Field(min_length=1, max_length=128)
    groups: str = Field(min_length=1, max_length=128)


class GroupsDisplay(BaseModel):
    id: int = Field(max_digits=3)
    groups_name: str
    groups: str

    class Config:
        orm_mode = True
