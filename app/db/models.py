from app.db.database import Base
from sqlalchemy import Column, Integer, LargeBinary, String
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.orm import relationship


class DbUser(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    email = Column(String)
    password = Column(LargeBinary)
    items = relationship("DbMaterial", back_populates="user")


class DbMaterial(Base):
    __tablename__ = "material"
    id = Column(Integer, primary_key=True, index=True)
    client = Column(String)
    position = Column(String)
    image_name = Column(String)
    text_name = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("DbUser", back_populates="items")


class DbGroups(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True, index=True)
    groups_name = Column(String)
    groups = Column(String)
