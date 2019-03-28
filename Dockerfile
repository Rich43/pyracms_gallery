FROM python:latest

# We copy this file first to leverage docker cache
COPY ./requirements.txt /code/gallery/requirements.txt

WORKDIR /code/gallery

RUN pip install -r requirements.txt

COPY . /code/gallery

RUN python setup.py bdist_wheel

