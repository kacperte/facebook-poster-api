FROM python:3.9

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN apt-get update && apt-get install -y xclip

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code/app