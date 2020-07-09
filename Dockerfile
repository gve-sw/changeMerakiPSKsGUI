FROM python:3
MAINTAINER jamah@cisco.com
RUN apt-get update -y
RUN apt-get install -y cron && apt-get install -y python-pip python-dev build-essential && apt-get install -y tzdata
COPY . /app
WORKDIR /app
#set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN pip install -r requirements.txt
#Start container with shells script to activate cron and views.py
ENTRYPOINT ["./start.sh"]
