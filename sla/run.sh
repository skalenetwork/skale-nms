#!/usr/bin/env bash

docker run -d --restart=unless-stopped --name skale-sla --env-file ../env.list -v /var/run/docker.sock:/var/run/docker.sock -v /skale_vol:/skale_vol -v skale_node_data:/skale_node_data --net=bridge skalelabshub/sla-manager:latest &&
echo "SKALE SLA agent container is up and running"