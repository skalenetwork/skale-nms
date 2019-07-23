#!/usr/bin/env bash

docker run -d --restart=always --name skale-events --env-file ../env.list -v /var/run/docker.sock:/var/run/docker.sock -v /skale_vol:/skale_vol --net=host skalelabshub/events-collect:latest &&
echo "SKALE Events Collector container is up and running"