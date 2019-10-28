#!/usr/bin/env bash
set -e

NAMES=("bounty-agent" "sla-manager")

for i in "${NAMES[@]}"
do
  echo "$i"

NAME=$i

REPO_NAME=skalelabshub/$NAME
IMAGE_NAME=$REPO_NAME:$VERSION
LATEST_IMAGE_NAME=$REPO_NAME:latest

: "${USERNAME?Need to set USERNAME}"
: "${PASSWORD?Need to set PASSWORD}"

echo "$PASSWORD" | docker login --username $USERNAME --password-stdin
echo "TEST!!!"
echo $IMAGE_NAME
docker push $IMAGE_NAME || exit $?
if [ "$RELEASE" = true ]
then
    docker push $LATEST_IMAGE_NAME || exit $?
fi

done

