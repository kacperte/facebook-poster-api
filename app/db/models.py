from app.db.database import Base
from sqlalchemy import Column, Integer, LargeBinary, String, DateTime, JSON
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.orm import relationship


class DbUser(Base):
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    email = Column(String)
    password = Column(LargeBinary)
    items = relationship("DbMaterial", back_populates="user")


class DbMaterial(Base):
    __tablename__ = "material"
    __table_args__ = {"extend_existing": True}
    id = Column(Integer, primary_key=True, index=True)
    client = Column(String)
    position = Column(String)
    image_name = Column(String)
    text_name = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("DbUser", back_populates="items")


class DbGroups(Base):
    __tablename__ = "groups"
    __table_args__ = {"extend_existing": True}
    id = Column(Integer, primary_key=True, index=True)
    groups_name = Column(String)
    groups = Column(String)


class DbJobStatus(Base):
    __tablename__ = "job_status"
    __table_args__ = {"extend_existing": True}
    id = Column(String, primary_key=True, index=True)
    date = Column(DateTime)
    groups_to_procced = Column(JSON)
