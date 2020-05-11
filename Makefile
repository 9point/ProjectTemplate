BASE_IMAGE_NAME=9point/ml-project
BASE_DOCKERFILE=Dockerfile.base

DOCKERFILE=Dockerfile

PROJECT_NAME=news-classifier
IMAGE_NAME=9point/ml-project-${PROJECT_NAME}

MAIN_PY=./src/main.py


.PHONY: protoc
protoc:
	bash scripts/protoc.sh


.PHONY: build_base_docker
build_base_docker:
	IMAGE_NAME=${BASE_IMAGE_NAME} DOCKERFILE=${BASE_DOCKERFILE} \
	bash scripts/build_docker.sh


.PHONY: build_docker
build_docker:
	IMAGE_NAME=${IMAGE_NAME} DOCKERFILE=${DOCKERFILE} \
	bash scripts/build_docker.sh


.PHONY: deploy_base_docker
deploy_base_docker:
	IMAGE_NAME=${BASE_IMAGE_NAME} DOCKERFILE=${BASE_DOCKERFILE} \
	bash scripts/deploy_docker.sh


.PHONY: deploy_docker
deploy_docker:
	IMAGE_NAME=${IMAGE_NAME} DOCKERFILE=${DOCKERFILE} bash scripts/deploy_docker.sh


.PHONY: register
register:
	IMAGE_NAME=${IMAGE_NAME} PROJECT_NAME=${PROJECT_NAME} MAIN_PY=${MAIN_PY} bash scripts/register.sh


.PHONY: start_workflow
start_workflow:
	IMAGE_NAME=${IMAGE_NAME} PROJECT_NAME=${PROJECT_NAME} WORKFLOW_NAME=${WORKFLOW_NAME} \
	bash scripts/start_workflow.sh

.PHONY: test
test:
	nosetests src