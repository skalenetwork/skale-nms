#!/usr/bin/env bash

set -e

: "${ETH_PRIVATE_KEY?Need to set ETH_PRIVATE_KEY}"
: "${DOCKER_USERNAME?Need to set DOCKER_USERNAME}"
: "${DOCKER_PASSWORD?Need to set DOCKER_PASSWORD}"
: "${MANAGER_BRANCH?Need to set MANAGER_BRANCH}"
: "${DB_ROOT_PASSWORD?Need to set DB_ROOT_PASSWORD}"
: "${DB_USER?Need to set DB_USER}"
: "${DB_PASSWORD?Need to set DB_PASSWORD}"
: "${DB_PORT?Need to set DB_PORT}"


# Run mysql docker container
echo "pwd:"
echo ${PWD}
docker run -d --restart=always --name skale-mysql -e MYSQL_ROOT_PASSWORD=$DB_ROOT_PASSWORD -e MYSQL_DATABASE=db_skale -e MYSQL_USER=$DB_USER -e MYSQL_PASSWORD=$DB_PASSWORD -v ${PWD}/test_data/init.sql:/docker-entrypoint-initdb.d/init.sql -p ${DB_PORT}:3306  mysql/mysql-server:5.7

# Run ganache
docker run -d --network host --name ganache trufflesuite/ganache-cli:v6.8.1-beta.0 \
    --account="0x${ETH_PRIVATE_KEY},100000000000000000000000000" -l 80000000 -b 1


echo "$DOCKER_PASSWORD" | docker login --username $DOCKER_USERNAME --password-stdin

export DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Deploy SKALE manager
docker pull skalenetwork/skale-manager:$MANAGER_BRANCH-latest
docker run \
    -v $DIR/contracts_data:/usr/src/manager/data \
    --network host \
    -e ENDPOINT=http://127.0.0.1:8545 \
    -e PRIVATE_KEY=$ETH_PRIVATE_KEY \
    skalenetwork/skale-manager:$MANAGER_BRANCH-latest \
    npx truffle migrate --network unique

# Prepare directories
whoami
echo $USER
echo $GITHUB_ACTOR
sudo mkdir -p /skale_vol/contracts_info
sudo chown -R $USER:$USER /skale_vol
sudo mkdir -p /skale_node_data
sudo chown -R $USER:$USER /skale_node_data
yes |sudo cp $DIR/contracts_data/unique.json /skale_vol/contracts_info/manager.json