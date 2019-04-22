#!/usr/bin/env bash

ver=0.1.8

docker build -t skalelabshub/bounty-agent:${ver} .. -f ../DockerfileBounty
echo "Skale Bounty agent v${ver} was built successfully" &&
echo "-----------------------------" &&
docker tag skalelabshub/bounty-agent:${ver} skalelabshub/bounty-agent:latest &&
echo "Bounty agent v${ver} was tagged to the latest successfully" &&
echo "-----------------------------" &&
echo "Pushing Bounty agent v${ver}" &&
docker push skalelabshub/bounty-agent:${ver} &&
echo "-----------------------------" &&
echo "Bounty agent v${ver} was pushed successfully" &&
echo "-----------------------------" &&
echo "Pushing Bounty agent latest" &&
docker push skalelabshub/bounty-agent:latest
echo "-----------------------------" &&
echo "Bounty agent latest was pushed successfully"
