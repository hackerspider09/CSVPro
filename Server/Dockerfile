FROM python:3.10-slim

ENV DIR=/home/app/

# where the code lives
WORKDIR $DIR

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


# install dependencies
RUN pip install --upgrade pip
# copy project
COPY . .

RUN pip install -r requirements.txt
