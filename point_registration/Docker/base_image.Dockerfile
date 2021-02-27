FROM python:3.8-slim AS base

RUN apt-get -y update

WORKDIR /point_matching
COPY config config

COPY requirements requirements
RUN pip install --upgrade pip
RUN pip install -r requirements/requirements.txt

COPY protodef ./protodef

RUN cd protodef && pip install .

# docker build -t base_point_registration:latest --rm --no-cache -f Docker/base_image.Dockerfile .