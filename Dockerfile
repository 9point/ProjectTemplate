FROM python:3

WORKDIR /app

COPY requirements.txt src/* ./

RUN pip install -r requirements.txt