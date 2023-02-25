from celery import Celery
import pika
from kombu import Queue, Exchange
from .agents.fb_bot import FacebookPoster

app = Celery("queue")
app.conf.broker_url = "redis://redis:6379/0"
app.conf.result_backend = "redis://redis:6379/0"
app.conf.task_routes = {"tasks.send_email_task": {"queue": "email-queue"}}
app.conf.task_queues = (
    Queue("default", Exchange("default"), routing_key="default"),
    Queue(
        "email-queue",
        Exchange("email-queue"),
        routing_key="email.tasks.send_email_task",
    ),
)
app.autodiscover_tasks()


@app.task(name="fb_poster")
def facebook_poster(login: str, password: str, groups: list):

    FacebookPoster(login=login, password=password, groups=groups).prepare_and_send_post(
        txt_name="copy/1.txt", img_name="content/2.jpg"
    )

    return {"message": "Success"}
