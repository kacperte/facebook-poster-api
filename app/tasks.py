from celery import Celery
import pika
from .agents.fb_bot import FacebookPoster

app = Celery("queue", broker="amqp://user:password@rabbitmq:5672")


@app.task(name="FB_poster")
def facebook_poster(login: str, password: str, groups: list):

    FacebookPoster(login=login, password=password, groups=groups).prepare_and_send_post(
        txt_name="copy/1.txt", img_name="content/2.jpg"
    )

    return {"message": "Success"}

"""
LOGIN_TRZEPIECINSKI = "kacper.trzepiecinski@hsswork.pl"
PASSWORD_TRZEPIECINSKI = "QuD*CC12d_Hju1!"
"""