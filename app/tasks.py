from celery import Celery
from .agents.fb_bot import FacebookPoster


app = Celery("queue")

app.conf.update(
    BROKER_URL="0.0.0.0:6379",
)


@app.task(name="FB_poster")
def facebook_poster(
    login: str,
    password: str,
):

    FacebookPoster(login=login, password=password).prepare_and_send_post(
        txt_name="content/test__test.txt", bucket_name="heroku-fb-poster", img_name="test__test.jfif"
    )

    return {"message": "Success"}


"""
LOGIN_TRZEPIECINSKI = "kacper.trzepiecinski@hsswork.pl"
PASSWORD_TRZEPIECINSKI = "QuD*CC12d_Hju1!"
"""
