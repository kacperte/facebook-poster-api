from pydantic import BaseModel
from typing import List


class Material(BaseModel):
    client: str
    position: str
    image_name: str
    text_name: str

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str
    email: str
    password: str


class UserDisplay(BaseModel):
    id: int
    username: str
    email: str

    items: List[Material] = []

    class Config:
        orm_mode = True


class User(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True


class MaterialBase(BaseModel):
    client: str
    position: str
    image_name: str
    text_name: str
    creator_id: int


class MaterialDisplay(BaseModel):
    id: int
    client: str
    position: str
    image_name: str
    text_name: str
    user: User

    class Config:
        orm_mode = True


class GroupsBase(BaseModel):
    groups_name: str
    groups: str


class GroupsDisplay(BaseModel):
    id: int
    groups_name: str
    groups: str

    class Config:
        orm_mode = True
