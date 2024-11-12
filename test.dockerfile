FROM python:3.8-slim-buster
WORKDIR /app

COPY . /app
RUN apt-get update && apt-get install -y git
RUN pip3 install -r requirements.txt
RUN pip install pytest pytest-flask


RUN [ "pytest" ]

