#!/usr/bin/env bash

ver=0.2.5

echo "Building SKALE SLA manager v${ver}..."
docker build -t skalelabshub/sla-manager:${ver} .. -f ../Dockerfile.sla &&
echo "SLA manager v${ver} was built successfully" &&
if [ "$1" == "p" ]
then
    echo "-----------------------------"
    echo "Prepare to publish to Docker Hub..."
    docker tag skalelabshub/sla-manager:${ver} skalelabshub/sla-manager:latest &&
    echo "SLA manager v${ver} was tagged to the latest successfully" &&
    echo "-----------------------------" &&
    echo "Pushing SLA manager v${ver}" &&
    docker push skalelabshub/sla-manager:${ver} &&
    echo "-----------------------------" &&
    echo "SLA manager v${ver} was pushed successfully" &&
    echo "-----------------------------" &&
    docker push skalelabshub/sla-manager:latest &&
    echo "-----------------------------" &&
    echo "SLA manager latest was pushed successfully"
fi