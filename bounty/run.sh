#!/usr/bin/env bash

docker run -d --restart=always --name skale-bounty --env-file ../env.list -v /var/run/docker.sock:/var/run/docker.sock -v /skale_vol:/skale_vol --net=host skalelabshub/bounty-agent:latest &&
echo "Skale Bounty collector container is up and running"
