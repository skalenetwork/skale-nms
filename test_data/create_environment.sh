#!/usr/bin/env bash

set -e

: "${ETH_PRIVATE_KEY?Need to set ETH_PRIVATE_KEY}"
: "${USERNAME?Need to set DOCKER_USERNAME}"
: "${PASSWORD?Need to set DOCKER_PASSWORD}"
: "${MANAGER_BRANCH?Need to set MANAGER_BRANCH}"
: "${DB_ROOT_PASSWORD?Need to set DB_ROOT_PASSWORD}"
: "${DB_USER?Need to set DB_USER}"
: "${DB_PASSWORD?Need to set DB_PASSWORD}"


# Run mysql docker container
docker run -d --restart=always --name skale-mysql -e MYSQL_ROOT_PASSWORD=$DB_ROOT_PASSWORD -e MYSQL_DATABASE=db_skale -e MYSQL_USER=$DB_USER -e MYSQL_PASSWORD=$DB_PASSWORD -v $TRAVIS_BUILD_DIR/test_data/init.sql:/docker-entrypoint-initdb.d/init.sql -p 3307:3306  mysql/mysql-server:5.7

# Run ganache
docker run -d --network host --name ganache trufflesuite/ganache-cli:v6.8.1-beta.0 \
    --account="${ETH_PRIVATE_KEY},100000000000000000000000000" -l 80000000


echo "$PASSWORD" | docker login --username $USERNAME --password-stdin

export DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Deploy SKALE manager
docker run \
    -v $DIR/contracts_data:/usr/src/manager/data \
    --network host -it \
    skalenetwork/skale-manager:$MANAGER_BRANCH-latest \
    npx truffle migrate --network test

# Prepare directories
sudo mkdir -p /skale_vol/contracts_info
sudo chown -R travis:travis /skale_vol
sudo mkdir -p /skale_node_data
sudo chown -R travis:travis /skale_node_data
yes |sudo cp $DIR/contracts_data/test.json /skale_vol/contracts_info/manager.json