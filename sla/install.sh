#!/usr/bin/env bash

# todo: check system requirements

# todo: check docker installation

#docker run -d --restart=always --name skale-sla -v /var/run/docker.sock:/var/run/docker.sock -v /skale_vol/config:/usr/src/sla/configs -v /skale_vol/logs:/usr/src/sla/logs --net=host skalelabshub/sla-manager:0.0.5
#docker run -d --restart=always --name sla-manager --env-file ./env.list -v /var/run/docker.sock:/var/run/docker.sock -v /skale_vol:/skale_vol --net=host skale-manager
docker run -d --restart=always --name sla-manager --env-file ./env.list -v /var/run/docker.sock:/var/run/docker.sock -v /skale_vol:/skale_vol --net=host skalelabshub/sla-manager:0.0.7
echo "Skale SLA container is up and running"