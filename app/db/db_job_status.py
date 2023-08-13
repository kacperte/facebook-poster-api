from sqlalchemy.orm.session import Session
from app.schemas import JobStatusBase
from app.db.models import DbJobStatus
from fastapi import HTTPException, status


def create_job_status(db: Session, request: JobStatusBase):
    """
    Creates new job status in the database
    """
    new_job_status = DbJobStatus(
        id=request.id, date=request.date, groups_to_procced=request.groups_to_procced
    )
    db.add(new_job_status)
    db.commit()
    db.refresh(new_job_status)

    return new_job_status


def get_all_job_status(db: Session):
    """
    Returns all job_status from database
    """
    return db.query(DbJobStatus).all()


def get_job_status_by_id(db: Session, id: str):
    """
    Returns job status by name
    """
    job_status = db.query(DbJobStatus).filter(DbJobStatus.id == id).first()
    if not job_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job status with id {id} not found",
        )
    return job_status


def update_job_status(db: Session, id: str, request: JobStatusBase):
    """
    Updates job status in the database
    """
    job_status = db.query(DbJobStatus).filter(DbJobStatus.id == id)
    if not job_status.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job status with id {id} not found",
        )
    job_status.update(
        {
            DbJobStatus.date: request.date,
            DbJobStatus.groups_to_procced: request.groups_to_procced,
        }
    )
    db.commit()
    return "ok"


def delete_job_status(db: Session, id: str):
    """
    Deletes job status in the database
    """
    job_status = db.query(DbJobStatus).filter(DbJobStatus.id == id).first()
    if not job_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job status with id {id} not found",
        )
    db.delete(job_status)
    db.commit()
    return "ok"
