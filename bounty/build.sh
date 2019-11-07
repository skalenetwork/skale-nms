#!/usr/bin/env bash

# Use for manual building/publishing of bounty-agent docker image
# Use "p" parameter to publish after build

VERSION=$(cat VERSION)-test
LINE="----------------------------------------"

echo "Building SKALE Bounty agent v${VERSION}..."
docker build -t skalelabshub/bounty-agent:${VERSION} . -f ./Dockerfile.bounty-agent &&
echo "Bounty agent v${VERSION} was built successfully" &&
if [ "$1" == "p" ]
then
    echo "$LINE"
    echo "Prepare to publish to Docker Hub..."
    docker tag skalelabshub/bounty-agent:${VERSION} skalelabshub/bounty-agent:latest &&
    echo "Bounty agent v${VERSION} was tagged to the latest successfully" &&
    echo "$LINE"
    echo "Pushing Bounty agent v${VERSION}" &&
    docker push skalelabshub/bounty-agent:${VERSION} &&
    echo "$LINE"
    echo "Bounty agent v${VERSION} was pushed successfully" &&
    echo "-----------------------------" &&
    echo "$LINE"
    docker push skalelabshub/bounty-agent:latest &&
    echo "$LINE"
    echo "Bounty agent latest was pushed successfully"
fi