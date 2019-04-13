#!/usr/bin/env bash

ver=0.1.7

docker build -t skalelabshub/sla-manager:${ver} .. -f ../DockerfileSLA
echo "Skale SLA manager v${ver} was built successfully" &&
echo "-----------------------------" &&
docker tag skalelabshub/sla-manager:${ver} skalelabshub/sla-manager:latest &&
echo "SLA manager v${ver} was tagged to the latest successfully" &&
echo "-----------------------------" &&
echo "Pushing SLA manager v${ver}" &&
docker push skalelabshub/sla-manager:${ver} &&
echo "-----------------------------" &&
echo "SLA manager v${ver} was pushed successfully" &&
echo "-----------------------------" &&
docker push skalelabshub/sla-manager:latest
echo "-----------------------------" &&
echo "SLA manager latest was pushed successfully"