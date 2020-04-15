IMAGE_NAME=brenmcnamara/test-project
PROJECT_NAME=test-project

protoc:
	bash scripts/protoc.sh

build_docker:
	IMAGE_NAME=${IMAGE_NAME} bash scripts/build_docker.sh

start_workflow:
	IMAGE_NAME=${IMAGE_NAME} PROJECT_NAME=${PROJECT_NAME} WORKFLOW_NAME=${WORKFLOW_NAME} \
	bash scripts/start_workflow.sh
	