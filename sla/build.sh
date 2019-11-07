#!/usr/bin/env bash

# Use for manual building/publishing of bounty-agent docker image
# Use "p" parameter to publish after build

VERSION=$(cat VERSION)-test
LINE="----------------------------------------"

echo "Building SKALE SLA agent v${VERSION}..."
docker build -t skalelabshub/sla-agent:${VERSION} . -f ./Dockerfile.sla-agent &&
echo "SLA agent v${VERSION} was built successfully" &&
if [ "$1" == "p" ]
then
    echo "$LINE"
    echo "Prepare to publish to Docker Hub..."
    docker tag skalelabshub/sla-agent:${VERSION} skalelabshub/sla-agent:latest &&
    echo "SLA agent v${VERSION} was tagged to the latest successfully" &&
    echo "$LINE"
    echo "Pushing SLA agent v${VERSION}" &&
    docker push skalelabshub/sla-agent:${VERSION} &&
    echo "$LINE"
    echo "SLA agent v${VERSION} was pushed successfully" &&
    echo "$LINE"
    docker push skalelabshub/sla-agent:latest &&
    echo "$LINE"
    echo "SLA agent latest was pushed successfully"
fi