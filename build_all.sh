#!/usr/bin/env bash

cd sla/
./build.sh "$1"
cd ../bounty/
./build.sh "$1"
