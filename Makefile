IMAGE_NAME=brenmcnamara/test-project

protoc:
	bash scripts/protoc.sh

build_docker:
	IMAGE_NAME=${IMAGE_NAME} bash scripts/build_docker.sh