from sqlalchemy.orm.session import Session
from app.schemas import MaterialBase
from app.db.models import DbMaterial
from fastapi import HTTPException, status


def create_material(db: Session, request: MaterialBase):
    new_group_post = DbMaterial(
        client=request.client,
        position=request.position,
        image=request.image,
        text=request.text,
        user_id=request.creator_id,
    )
    db.add(new_group_post)
    db.commit()
    db.refresh(new_group_post)
    return new_group_post


def get_all_materials(db: Session):
    return db.query(DbMaterial).all()


def get_material(db: Session, id: int):
    group_post = db.query(DbMaterial).filter(DbMaterial.id == id).first()
    if not group_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group post with id {id} not found",
        )
    return group_post


def get_all_materials_by_client(db: Session, client: str):
    group_post = db.query(DbMaterial).filter(DbMaterial.client == client).all()
    if not group_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group post with client name {client} not found",
        )
    return group_post


def update_material(db: Session, id: int, request: MaterialBase):
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
            DbMaterial.image: request.image,
            DbMaterial.text: request.text,
        }
    )
    db.commit()
    return "ok"


def delete_material(db: Session, id: int):
    group_post = db.query(DbMaterial).filter(DbMaterial.id == id).first()
    if not group_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group post with id {id} not found",
        )
    db.delete(group_post)
    db.commit()
    return "ok"
