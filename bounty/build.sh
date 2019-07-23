#!/usr/bin/env bash

ver=0.2.4

echo "Building SKALE Bounty agent v${ver}..."
docker build -t skalelabshub/bounty-agent:${ver} .. -f ../Dockerfile.bounty &&
echo "Bounty agent v${ver} was built successfully" &&
if [ "$1" == "p" ]
then
    echo "-----------------------------"
    echo "Prepare to publish to Docker Hub..."
    docker tag skalelabshub/bounty-agent:${ver} skalelabshub/bounty-agent:latest &&
    echo "Bounty agent v${ver} was tagged to the latest successfully" &&
    echo "-----------------------------" &&
    echo "Pushing Bounty agent v${ver}" &&
    docker push skalelabshub/bounty-agent:${ver} &&
    echo "-----------------------------" &&
    echo "Bounty agent v${ver} was pushed successfully" &&
    echo "-----------------------------" &&
    echo "Pushing Bounty agent latest" &&
    docker push skalelabshub/bounty-agent:latest &&
    echo "-----------------------------" &&
    echo "Bounty agent latest was pushed successfully"
fi