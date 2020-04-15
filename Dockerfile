FROM python:3
WORKDIR /app
COPY requirements.txt src/ ./
RUN make protoc && pip install -r requirements.txt