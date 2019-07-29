#!/usr/bin/env bash

#curl -sL https://deb.nodesource.com/setup_10.x -o nodesource_setup.sh &&
sudo apt-get update &&
#sudo bash nodesource_setup.sh &&
#sudo apt-get install -y nodejs &&
sudo apt-get install -y build-essential &&
git clone -b feature/alpine-team https://$GITHUB_TOKEN\@github.com/skalenetwork/skale-manager.git &&
cd skale-manager &&
npm install &&
PRIVATE_KEY=$ETH_PRIVATE_KEY ENDPOINT="http://127.0.0.1:1919"  ./node_modules/.bin/truffle migrate --network unique

