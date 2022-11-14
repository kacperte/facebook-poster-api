from sqlalchemy.orm.session import Session
from app.schemas import Groups
from app.db.models import DbGroups
from fastapi import HTTPException, status


def create_gropus(db: Session, request: Groups):
    new_grups = DbGroups(
        groups_name=request.groups_name,
        groups=request.groups,
    )
    db.add(new_grups)
    db.commit()
    db.refresh(new_grups)
    return new_grups


def get_all_groups(db: Session):
    return db.query(DbGroups).all()


def get_user_by_groups_name(db: Session, groups_name: str):
    groups = db.query(DbGroups).filter(DbGroups.groups_name == groups_name).first()
    if not groups:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {groups_name} not found",
        )
    return groups


def update_groups(db: Session, groups_name: str, request: Groups):
    groups = db.query(DbGroups).filter(DbGroups.groups_name == groups_name)
    if not groups.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {groups_name} not found",
        )
    groups.update(
        {
            DbGroups.groups_name: request.groups_name,
            DbGroups.groups: request.groups,
        }
    )
    db.commit()
    return "ok"


def delete_groups(db: Session, groups_name: str):
    groups = db.query(DbGroups).filter(DbGroups.groups_name == groups_name).first()
    if not groups:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {groups_name} not found",
        )
    db.delete(groups)
    db.commit()
    return "ok"
