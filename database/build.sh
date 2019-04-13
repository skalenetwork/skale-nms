#!/usr/bin/env bash

ver=0.0.5

docker build -t skalelabshub/mysql:${ver} .
echo "Skale MySQL docker image v${ver} was built successfully" &&
echo "-----------------------------" &&
docker tag skalelabshub/mysql:${ver} skalelabshub/mysql:latest &&
echo "Skale MySQL docker image v${ver} was tagged to the latest successfully" &&
echo "-----------------------------" &&
echo "Pushing Skale MySQL docker image v${ver}" &&
docker push skalelabshub/mysql:${ver} &&
echo "-----------------------------" &&
echo "Skale MySQL docker image v${ver} was pushed successfully" &&
echo "-----------------------------" &&
echo "Pushing Skale MySQL docker image latest" &&
docker push skalelabshub/mysql:latest
echo "-----------------------------" &&
echo "Skale MySQL docker image latest was pushed successfully"