FROM python:3.8-slim-buster
WORKDIR /app

COPY requirements.txt requirements.txt

RUN apt-get update && apt-get install -y git
RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 5000

CMD [ "python3" , "-u", "main.py" ]