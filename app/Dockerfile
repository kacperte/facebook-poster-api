FROM python:3.9

ENV PYTHONPATH=/code
EXPOSE 3000

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code/app

CMD uvicorn app.main:app --host 0.0.0.0 --reload