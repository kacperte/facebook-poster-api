import logging
from celery import Celery
from .agents.fb_bot import FacebookPoster


app = Celery("queue", broker="amqp://user:password@rabbitmq-service:5672")

logger = logging.getLogger(__name__)


@app.task(name="FB_poster", max_retries=3, default_retry_delay=10)
def facebook_poster(login: str, password: str, groups: list):
    try:
        FacebookPoster(
            login=login, password=password, groups=groups
        ).prepare_and_send_post(txt_name="copy/2.txt", img_name="content/2.jpg")
        logger.info("Task FB_poster completed successfully")
        return {"message": "Success"}
    except Exception as exc:
        logger.exception("An error occurred during task FB_poster: %s", exc)
        raise facebook_poster.retry(exc=exc)
