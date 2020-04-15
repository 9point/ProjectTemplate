FROM python:3

WORKDIR /app

COPY Makefile requirements.txt src/ ./

# TODO: Should have a separate build phase.
COPY scripts/ ./scripts/

# TODO: Should have a separate build phase.
COPY proto/ ./proto

RUN pip install grpcio-tools && make protoc && pip install -r requirements.txt