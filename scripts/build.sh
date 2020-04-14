#!/usr/bin/env bash

set -e

echo ""
echo "------------------------------------"
echo "           DOCKER BUILD"
echo "------------------------------------"
echo ""

# Do not push if there are unstaged git changes
CHANGED=$(git status --porcelain)
if [ -n "$CHANGED" ]; then
  echo "Please commit git changes before pushing to a registry"
  exit 1
fi


GIT_SHA=$(git rev-parse HEAD)

IMAGE_TAG_WITH_SHA="${IMAGE_NAME}:${GIT_SHA}"

RELEASE_SEMVER=$(git describe --tags --exact-match "$GIT_SHA" 2>/dev/null) || true
if [ -n "$RELEASE_SEMVER" ]; then
  IMAGE_TAG_WITH_SEMVER="${IMAGE_NAME}:${RELEASE_SEMVER}${IMAGE_TAG_SUFFIX}"
fi

# build the image
docker build -t "$IMAGE_TAG_WITH_SHA" -t "$IMAGE_NAME:latest" --build-arg IMAGE_TAG="${IMAGE_TAG_WITH_SHA}" .
echo "${IMAGE_TAG_WITH_SHA} built locally."

if [ -n "${DOCKER_REGISTRY_PASSWORD}" ]; then
  docker login --username="$DOCKER_REGISTRY_USERNAME" --password="$DOCKER_REGISTRY_PASSWORD"
fi

docker tag "$IMAGE_TAG_WITH_SHA" "${IMAGE_TAG_WITH_SHA}"

docker push "${IMAGE_TAG_WITH_SHA}"
echo "${IMAGE_TAG_WITH_SHA} pushed to remote."

# If the current commit has a semver tag, also push the images with the semver tag
if [ -n "$RELEASE_SEMVER" ]; then

  docker tag "$IMAGE_TAG_WITH_SHA" "${IMAGE_TAG_WITH_SEMVER}"

  docker push "${IMAGE_TAG_WITH_SEMVER}"
  echo "${IMAGE_TAG_WITH_SEMVER} pushed to remote."

fi
