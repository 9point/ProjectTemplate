FROM 9point/ml-project

WORKDIR /app

COPY Makefile src/ ./

# TODO: Should have a separate build phase.
COPY scripts/ ./scripts/

# TODO: Should have a separate build phase.
COPY proto/ ./proto

RUN make protoc