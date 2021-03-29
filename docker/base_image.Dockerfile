FROM python:3.8-slim AS base

RUN apt-get -y update

WORKDIR /master_thesis_backend

COPY python_requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

FROM base 
COPY protobuf ./protobuf

RUN cat requirements.txt
RUN cd protobuf 
WORKDIR /master_thesis_backend/protobuf
RUN pip install .

# docker build -t base_master_thesis:latest --rm --no-cache -f docker/base_image.Dockerfile .