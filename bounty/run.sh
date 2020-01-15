#!/usr/bin/env bash

# For test local run only

docker run -d --restart=unless-stopped --name skale_bounty --env-file ./env.list -v /var/run/docker.sock:/var/run/docker.sock -v /skale_vol:/skale_vol -v skale_node_data:/skale_node_data --net=host skalenetwork/bounty-agent:latest &&
echo "SKALE Bounty collector container is up and running"
