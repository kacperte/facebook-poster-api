from sqlalchemy.orm.session import Session
from app.schemas import GroupsBase
from app.db.models import DbGroups
from fastapi import HTTPException, status


def create_groups(db: Session, request: GroupsBase):
    """
    Creates new groups in the database
    """
    new_groups = DbGroups(
        groups_name=request.groups_name,
        groups=request.groups,
    )
    db.add(new_groups)
    db.commit()
    db.refresh(new_groups)
    return new_groups


def get_all_groups(db: Session):
    """
    Returns all groups from database
    """
    return db.query(DbGroups).all()


def get_groups_by_name(db: Session, groups_name: str):
    """
    Returns groups by name
    """
    groups = db.query(DbGroups).filter(DbGroups.groups_name == groups_name).first()
    if not groups:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group with gropus name {groups_name} not found",
        )
    return groups


def update_groups(db: Session, id: int, request: GroupsBase):
    """
    Updates groups in the database
    """
    groups = db.query(DbGroups).filter(DbGroups.id == id)
    if not groups.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group with id {id} not found",
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
    """
    Deletes groups in the database
    """
    groups = db.query(DbGroups).filter(DbGroups.groups_name == groups_name).first()
    if not groups:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group with gropus name {groups_name} not found",
        )
    db.delete(groups)
    db.commit()
    return "ok"
