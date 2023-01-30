FROM python:3.11-slim

WORKDIR /webdvl

COPY requirements.txt requirements.txt

RUN apt-get update \
    && pip3 install -r requirements.txt

USER 1002

COPY . .