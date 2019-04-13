#!/usr/bin/env bash

# todo: check system requirements

# todo: check docker installation

docker run -d --restart=always --name skale-bounty --env-file ./env.list -v /var/run/docker.sock:/var/run/docker.sock -v /skale_vol:/skale_vol --net=host skalelabshub/bounty-agent:0.0.8
echo "Skale SLA container is up and running"
