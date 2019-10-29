#!/usr/bin/env bash

set -e

#NAME=bounty-agent
NAME=$1
#VERSION=0.2.9
REPO_NAME=skalelabshub/$NAME
IMAGE_NAME=$REPO_NAME:$VERSION
LATEST_IMAGE_NAME=$REPO_NAME:latest

: "${VERSION?Need to set VERSION}"

echo "Building $IMAGE_NAME..."
#docker build -t $IMAGE_NAME . || exit $?
docker build -t $IMAGE_NAME . -f ./Dockerfile.bounty || exit $?

if [ "$RELEASE" = true ]
then
    docker tag $IMAGE_NAME $LATEST_IMAGE_NAME
fi

echo "========================================================================================="
echo "Built $IMAGE_NAME"
