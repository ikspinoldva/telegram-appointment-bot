FROM python:3.10

WORKDIR /home

ENV API_TOKEN = ""
ENV ADMIN_ID = ""

ENV TZ=Europe/Warsaw
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN pip install -U pip aiogram pytz asyncio && apt-get update && apt-get install sqlite3
COPY *.py ./
COPY createdb.sql ./

ENTRYPOINT ["python", "server.py"]