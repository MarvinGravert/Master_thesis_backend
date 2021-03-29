FROM python:3.8-slim AS base

RUN apt-get -y update
RUN apt-get install libhdf5-dev -y
RUN apt-get install libhdf5-serial-dev -y
RUN apt-get install libatlas-base-dev -y
# RUN apt-get install libjasper-dev -y
RUN apt-get install libqtgui4 -y 
RUN apt-get install libqt4-test -y
RUN apt-get install ffmpeg libsm6 libxext6  -y

WORKDIR /master_thesis_backend

COPY python_requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

FROM base 
COPY protobuf ./protobuf

RUN cat requirements.txt
RUN cd protobuf && pip install -e . 

# docker build -t base_master_thesis:latest --rm --no-cache -f docker/base_image.Dockerfile .