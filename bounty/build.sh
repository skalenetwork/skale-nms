#!/usr/bin/env bash

# Use for manual building/publishing of bounty-agent docker image
# Use "p" parameter to publish after build

VERSION=$(cat VERSION)
TAG=$VERSION-test.0
LINE="----------------------------------------"

echo "Building SKALE Bounty agent v${VERSION}..."
docker build -t skalenetwork/bounty-agent:${TAG} . -f ./Dockerfile.bounty-agent &&
echo "Bounty agent v${VERSION} was built successfully" &&
if [ "$1" == "p" ]
then
    echo "$LINE"
    echo "Prepare to publish to Docker Hub..."
    docker tag skalenetwork/bounty-agent:${TAG} skalenetwork/bounty-agent:latest &&
    echo "Bounty agent v${VERSION} was tagged to the latest successfully" &&
    echo "$LINE"
    echo "Pushing Bounty agent v${VERSION}" &&
    docker push skalenetwork/bounty-agent:${TAG} &&
    echo "$LINE"
    echo "Bounty agent v${VERSION} was pushed successfully" &&
    echo "$LINE"
    docker push skalenetwork/bounty-agent:latest &&
    echo "$LINE"
    echo "Bounty agent tagged latest was pushed successfully"
fi