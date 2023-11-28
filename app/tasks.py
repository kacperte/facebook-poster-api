import logging
from celery import Celery
from .agents.fb_bot import FacebookPoster
from app.db import db_job_status
from app.db.database import SessionLocal


app = Celery("queue", broker="amqp://user:password@rabbitmq-service:5672")
app.conf.update(
    worker_log_level='WARNING'
)

logger = logging.getLogger(__name__)


@app.task(name="FB_poster", max_retries=3, default_retry_delay=10)
def facebook_poster(
    login: str,
    password: str,
    image_name: str,
    text_name: str,
    id: str,
):
    # Tutaj pobierać dopiero grupy, aby nie były przekazane wcześniej w formie zmiennej
    with SessionLocal() as db:
        job_status_record = db_job_status.get_job_status_by_id(id=id, db=db)
        groups = job_status_record.groups_to_procced

    try:
        FacebookPoster(
            login=login, password=password, groups=groups
        ).prepare_and_send_post(txt_name=text_name, img_name=image_name, group_id=id)
        logger.info("Task FB_poster completed successfully")
        return {"message": "Success"}
    except Exception as exc:
        logger.exception("An error occurred during task FB_poster: %s", exc)
        raise facebook_poster.retry(exc=exc)
