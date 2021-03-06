#!/usr/bin/env bash

# Use for manual building/publishing of bounty-agent docker image
# Use "p" parameter to publish after build

VERSION=$(cat VERSION)
TAG=$VERSION-test.0
LINE="----------------------------------------"

echo "Building SKALE SLA agent v${VERSION}..."
docker build -t skalenetwork/sla-agent:${TAG} . -f ./Dockerfile.sla-agent &&
echo "SLA agent v${VERSION} was built successfully" &&
if [ "$1" == "p" ]
then
    echo "$LINE"
    echo "Prepare to publish to Docker Hub..."
    docker tag skalenetwork/sla-agent:${TAG} skalenetwork/sla-agent:latest &&
    echo "SLA agent v${VERSION} was tagged to the latest successfully" &&
    echo "$LINE"
    echo "Pushing SLA agent v${VERSION}" &&
    docker push skalenetwork/sla-agent:${TAG} &&
    echo "$LINE"
    echo "SLA agent v${VERSION} was pushed successfully" &&
    echo "$LINE"
    docker push skalenetwork/sla-agent:latest &&
    echo "$LINE"
    echo "SLA agent tagged latest was pushed successfully"
fi