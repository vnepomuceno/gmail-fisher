FROM python:3.9-buster

ENV PKG_HOME=/package

WORKDIR ${PKG_HOME}

COPY ./Pipfile* ${PKG_HOME}/

RUN \
    apt-get update && \
    pip install --upgrade pip pipenv && \
    pipenv install

COPY . ${PKG_HOME}/
