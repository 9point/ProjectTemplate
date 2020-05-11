#!/usr/bin/env bash

set -e

echo "Registering Project..."

# Do not push if there are unstaged git changes
CHANGED=$(git status --porcelain)
# if [ -n "$CHANGED" ]; then
#   echo "Please commit git changes before registering the project"
#   exit 1
# fi


GIT_SHA=$(git rev-parse HEAD)

IMAGE_TAG_WITH_SHA="${IMAGE_NAME}:${GIT_SHA}"

IMAGE_EXISTS=$(docker images -q ${IMAGE_TAG_WITH_SHA} | wc -l | tr -d '[[:space:]]')

# if [ $IMAGE_EXISTS -eq "0" ]; then
#   echo "Must build and deploy docker image before it can be registered"
#   exit 1
# fi

# Assuming the image has already been deployed to the registry.

export PROJECT_NAME=${PROJECT_NAME}
export IMAGE_NAME=${IMAGE_TAG_WITH_SHA}

python ${MAIN_PY} register
