#!/usr/bin/env bash

# For test local run only

docker run -d --restart=unless-stopped --name skale_sla --env-file ./env.list -v /var/run/docker.sock:/var/run/docker.sock -v /skale_vol:/skale_vol -v skale_node_data:/skale_node_data --net=host skalelabshub/sla-agent:latest &&
echo "SKALE SLA agent container is up and running"