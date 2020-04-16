BASE_IMAGE_NAME=brenmcnamara/ml-base
BASE_DOCKERFILE=Dockerfile.base

IMAGE_NAME=brenmcnamara/test-project
DOCKERFILE=Dockerfile

PROJECT_NAME=test-project

protoc:
	bash scripts/protoc.sh

build_docker:
	IMAGE_NAME=${IMAGE_NAME} DOCKERFILE=${DOCKERFILE} \
	bash scripts/build_docker.sh

build_base_docker:
	IMAGE_NAME=${BASE_IMAGE_NAME} DOCKERFILE=${BASE_DOCKERFILE} \
	bash scripts/build_docker.sh

start_workflow:
	IMAGE_NAME=${IMAGE_NAME} PROJECT_NAME=${PROJECT_NAME} WORKFLOW_NAME=${WORKFLOW_NAME} \
	bash scripts/start_workflow.sh
	