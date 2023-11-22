FROM python:3.8.18-slim-bookworm

ENV PYTHONUNBUFFERED 1
ARG DEV_BUILD
WORKDIR /app

RUN apt update \
  && apt install -y build-essential gettext gnupg \
     libatlas-base-dev libgdal-dev \
     libgcc-11-dev libgfortran-11-dev \
     libspatialindex-dev \
     make python3-dev wget \
  && apt upgrade -y \
  && apt purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && apt clean \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --no-cache-dir -U pip \
  && pip install --no-cache-dir -Ur /app/requirements.txt

COPY . /app/
