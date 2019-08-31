#!/usr/bin/env bash

# commented lines have to be uncommented when script is used on clear Ubuntu (not Travis)

#curl -sL https://deb.nodesource.com/setup_10.x -o nodesource_setup.sh &&
sudo apt-get update && # comment this line if use clear Ubuntu (not Travis)
#sudo bash nodesource_setup.sh &&
#sudo apt-get install -y nodejs &&
sudo apt-get install -y build-essential &&
git clone -b feature/alpine-team https://$GITHUB_TOKEN\@github.com/skalenetwork/skale-manager.git &&
cd skale-manager &&
npm install &&
PRIVATE_KEY=$ETH_PRIVATE_KEY ENDPOINT=$ENDPOINT  ./node_modules/.bin/truffle migrate --network unique

