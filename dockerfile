# pull official base image
ARG BASE_IMAGE=python:3.8.3-slim-buster

FROM ${BASE_IMAGE} AS requirements-image

# set working directory
WORKDIR /usr/src/app

# set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get -y install netcat gcc cron \
    && apt-get clean

# install python dependencies
RUN pip install --upgrade pip
RUN pip install pipenv pytest
COPY Pipfile* ./
RUN pipenv lock -r --dev > requirements.txt

# add app
FROM ${BASE_IMAGE} AS compile-image
WORKDIR /usr/src/app
COPY --from=requirements-image /usr/src/app/requirements.txt /usr/src/app/requirements.txt

# set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
    python3 \
    netcat \
    gcc \
    cron \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && cd /tmp \
    && curl -O https://bootstrap.pypa.io/get-pip.py \
    && python3 get-pip.py

RUN python3 -m venv /home/venv
ENV PATH="/home/venv/bin:$PATH"
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1 \
    && update-alternatives --install /usr/local/bin/pip pip /usr/local/bin/pip3 1

RUN pip install --no-cache-dir -r requirements.txt


FROM ${BASE_IMAGE} AS runtime-image
ENV PYTHONUNBUFFERED TRUE
COPY --from=compile-image /home/venv /home/venv
ENV PATH="/home/venv/bin:$PATH"

WORKDIR /usr/src/app

EXPOSE 80
COPY . .
