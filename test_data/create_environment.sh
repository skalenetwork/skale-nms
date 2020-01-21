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

## Run geth docker container
git clone -b one-node-for-tests https://$GITHUB_TOKEN\@github.com/skalenetwork/skale-infrastructure.git &&
cd skale-infrastructure/geth &&
export BOOTNODE_ID=52e78c5a317119a240ed80e94ed301876f87f9ca62b35b689376f1dc9fdb1b11b06eb3d724e1eea6651bd33ada569b5aa084833cff8f7dbde658844424dd74f9 BOOTNODE_IP="127.0.0.1" NODE_KEY_HEX=ab6180cce6f61fa0258295322bd3f6c959582f6c73f2b1bc0d93b71bfa7fdef6 &&
docker-compose up -d &&


# Deploy SKALE manager
cd $TRAVIS_BUILD_DIR &&
git clone -b develop https://$GITHUB_TOKEN\@github.com/skalenetwork/skale-manager.git &&
cd skale-manager &&
yarn install &&

echo "$PASSWORD" | docker login --username $USERNAME --password-stdin

export DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

docker run \
    -v $DIR/contracts_data:/usr/src/manager/data \
    --network host -it \
    skalenetwork/skale-manager:$MANAGER_BRANCH-latest \
    PRIVATE_KEY=$ETH_PRIVATE_KEY ENDPOINT=$ENDPOINT npx truffle migrate --network unique

#PRIVATE_KEY=$ETH_PRIVATE_KEY ENDPOINT=$ENDPOINT  ./node_modules/.bin/truffle migrate --network unique

# Prepare directories
sudo mkdir -p /skale_vol/contracts_info
sudo chown -R travis:travis /skale_vol
sudo mkdir -p /skale_node_data
sudo chown -R travis:travis /skale_node_data
#yes |sudo cp $TRAVIS_BUILD_DIR/skale-manager/data/unique.json /skale_vol/contracts_info/manager.json
yes |sudo cp $DIR/contracts_data/unique.json /skale_vol/contracts_info/manager.json