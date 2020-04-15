#!/bin/bash

PROTO_DIR=./proto/
CODEGEN_DIR=./src/static_codegen/

PROTO_FILES=$(ls ${PROTO_DIR})

mkdir -p src/static_codegen

for PROTO_FILE in $PROTO_FILES
do
echo "Compiling ${PROTO_FILE}..."
python -m grpc_tools.protoc -I${CODEGEN_DIR} \
       --python_out=${CODEGEN_DIR} \
       --grpc_python_out=${CODEGEN_DIR} \
       --proto_path proto/ \
       ${PROTO_FILE}

done

# This is a hack to get around a bug with protoc compiler with handling
# relative paths in python: https://github.com/protocolbuffers/protobuf/issues/1491
printf "import os\nimport sys\nsys.path.append(os.path.dirname(__file__))" > ${CODEGEN_DIR}__init__.py