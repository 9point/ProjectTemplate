FROM brenmcnamara/ml-base

WORKDIR /app

COPY Makefile src/ ./

# TODO: Should have a separate build phase.
COPY scripts/ ./scripts/

# TODO: Should have a separate build phase.
COPY proto/ ./proto

RUN make protoc