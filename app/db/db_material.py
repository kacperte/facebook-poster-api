from sqlalchemy.orm.session import Session
from app.schemas import MaterialBase
from app.db.models import DbMaterial
from fastapi import HTTPException, status


def create_material(db: Session, request: MaterialBase):
    """
    Creates new material in the database
    """
    new_group_post = DbMaterial(
        client=request.client,
        position=request.position,
        image_name=request.image_name,
        text_name=request.text_name,
        user_id=request.creator_id,
    )
    db.add(new_group_post)
    db.commit()
    db.refresh(new_group_post)

    return new_group_post


def get_all_materials(db: Session):
    """
    Returns all materials from the database
    """
    return db.query(DbMaterial).all()


def get_material(db: Session, id: int):
    """
    Returns material by id
    """
    group_post = db.query(DbMaterial).filter(DbMaterial.id == id).first()
    if not group_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group post with id {id} not found",
        )
    return group_post


def get_all_materials_by_client(db: Session, client: str):
    """
    Returns all materials by client
    """
    materials = db.query(DbMaterial).filter(DbMaterial.client == client).all()
    if not materials:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Materials from client {client} not found",
        )
    return materials


def update_material(db: Session, id: int, request: MaterialBase):
    """
    Updates material in the database
    """
    group_post = db.query(DbMaterial).filter(DbMaterial.id == id)
    if not group_post.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group post with id {id} not found",
        )
    group_post.update(
        {
            DbMaterial.client: request.client,
            DbMaterial.position: request.position,
            DbMaterial.image: request.image_name,
            DbMaterial.text: request.text_name,
        }
    )
    db.commit()
    return group_post.first()


def delete_material(db: Session, id: int):
    """
    Deletes material from the database
    """
    group_post = db.query(DbMaterial).filter(DbMaterial.id == id).first()
    if not group_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group post with id {id} not found",
        )
    db.delete(group_post)
    db.commit()
    return group_post
