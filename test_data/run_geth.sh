#!/usr/bin/env bash

git clone -b one-node-for-tests https://$GITHUB_TOKEN\@github.com/skalenetwork/skale-infrastructure.git &&
cd skale-infrastructure/geth &&
export BOOTNODE_ID=52e78c5a317119a240ed80e94ed301876f87f9ca62b35b689376f1dc9fdb1b11b06eb3d724e1eea6651bd33ada569b5aa084833cff8f7dbde658844424dd74f9 BOOTNODE_IP="127.0.0.1" NODE_KEY_HEX=ab6180cce6f61fa0258295322bd3f6c959582f6c73f2b1bc0d93b71bfa7fdef6 &&
docker-compose up -d
