FROM python:3.8-slim AS base

RUN apt-get -y update

WORKDIR /master_thesis_backend

COPY python_requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY protobuf ./protobuf

RUN cd protobuf && pip install .

# docker build -t base_master_thesis:latest --rm --no-cache -f docker/base_image.Dockerfile .