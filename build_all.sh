#!/usr/bin/env bash

# Use for manual building/publishing of sla/bounty agents docker images
# Use "p" parameter to publish after build

sla/build.sh "$1"
bounty/build.sh "$1"
