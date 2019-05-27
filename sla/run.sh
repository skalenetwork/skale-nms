#!/usr/bin/env bash

docker run -d --restart=always --name skale-sla1 --env-file ../env.list -v /var/run/docker.sock:/var/run/docker.sock -v /skale_vol:/skale_vol --net=host skalelabshub/sla-manager:latest &&
echo "Skale SLA manager container is up and running"