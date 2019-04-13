#!/usr/bin/env bash

# todo: check system requirements

# todo: check docker installation

docker run -d --restart=always --name skale-mysql -e MYSQL_ROOT_PASSWORD=password -e MYSQL_DATABASE=test -e MYSQL_USER=user -e MYSQL_PASSWORD=pass  --net=host skalelabshub/mysql:0.0.5
echo "Skale SLA MySQL container is up and running"