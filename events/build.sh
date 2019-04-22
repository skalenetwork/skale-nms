#!/usr/bin/env bash

ver=0.1.8

docker build -t skalelabshub/events-collect:${ver} .. -f ../DockerfileEvents
echo "Skale Events collector v${ver} was built successfully" &&
echo "-----------------------------" &&
docker tag skalelabshub/events-collect:${ver} skalelabshub/events-collect:latest &&
echo "Events collector v${ver} was tagged to the latest successfully" &&
echo "-----------------------------" &&
echo "Pushing Events collector v${ver}" &&
docker push skalelabshub/events-collect:${ver} &&
echo "-----------------------------" &&
echo "Events collector v${ver} was pushed successfully" &&
echo "-----------------------------" &&
echo "Pushing Events collector latest" &&
docker push skalelabshub/events-collect:latest
echo "-----------------------------" &&
echo "Events collector latest was pushed successfully"
