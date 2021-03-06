
# NOTE: `SKALE-NMS` is deprecated and no longer in active maintenance. Please see [sla-agent](https://github.com/skalenetwork/sla-agent) and [bounty-agent](https://github.com/skalenetwork/bounty-agent) repos.</p>

## SKALE Node Monitoring Service (NMS)

SKALE NMS is comprised of the SLA agent and Bounty collector, which are parts of the [SKALE node](https://github.com/skalenetwork/skale-node).

Every SKALE node has a NMS group of N (e.g. 24) other nodes in the network randomly assigned to it. NMS groups regularly audit node downtime and latency at predetermined periods (e.g. five minutes), log these measurements to their local databases, and submit average metrics to the SKALE Manager contract (SMC) once for every reward period - epoch (e.g. 30 days). Every node is rewarded for its validation efforts, based on results sent by NMS group of this node, at the end of each epoch.

## An important note about production readiness

SKALE-NMS is still in active development and therefore should be regarded as alpha software. The development is still subject to security hardening, further testing, and breaking changes. This repository has not yet been reviewed or audited for security.

## Project structure

Code of SLA agent and Bounty collector are located in [sla](https://github.com/skalenetwork/skale-nms/tree/develop/sla) and [bounty](https://github.com/skalenetwork/skale-nms/tree/develop/bounty) directories respectively.  

## SLA agent

SLA agent runs on every node of SKALE network, periodically requests a list of nodes to monitor from SKALE Manager contract, conducts monitoring of these other nodes (node downtime and latency so far), logs these measurements, and sends average metrics per epoch to SMC (once for every epoch).

### Development

#### Requirements

Python >= 3.6.5

#### Install dependencies

```bash
pip install -r sla/requirements.txt
```

#### Testing

##### Requirements for tests

To run tests locally, you need to have MySQL v5.7 installed and database 'db_skale' and some tables created (see below). Also you have to change the name of `test_data/.env_template` to `test_data/.env` and fill it out with your environment variables:

    ETH_PRIVATE_KEY='YOUR_PRIVATE_KEY' 
    DB_ROOT_PASSWORD='YOUR_MYSQL_ROOT_PASSWORD'
    DB_USER='YOUR_MYSQL_USER'
    DB_PASSWORD='YOUR_MYSQL_PASSWORD'

As for using MySQL you have two options:

1.  Use MySQL docker container (recommended). In this case:
    \- install [Docker CE](https://docs.docker.com/install/) v18.06? (if you haven't it installed)
    \- run following command:

    docker run -d --restart=always --name skale-mysql -e MYSQL_ROOT_PASSWORD=$DB_ROOT_PASSWORD 
    \-e MYSQL_DATABASE=db_skale -e MYSQL_USER=$DB_USER -e MYSQL_PASSWORD=$DB_PASSWORD 
    \-v test_data/init.sql:/docker-entrypoint-initdb.d/init.sql -p 3307:3306  mysql/mysql-server:5.7

2.  If you already have MySQL v5.7 installed on your PC - create db named 'db_skale' and tables with a help of this [init.sql](https://github.com/skalenetwork/skale-nms/blob/develop/test_data/init.sql) file. Keep in mind that SLA agent uses MySQL on port 3307 (not 3306)

##### Run tests

    py.test -v tests/test_sla.py

### Build and run

For building SLA agent docker container and pushing it to Docker Hub use:

```bash
cd sla
sh ./build.sh
```

Run docker container locally:

```bash
cd sla
sh ./install.sh
```

## Bounty collector

Bounty agent runs on every node of SKALE network and handles the collection of the bounty over time from the SKALE Manager for its validation efforts.

### Development

#### Requirements

Python >= 3.6.5

#### Install dependencies

    pip install -r bounty/requirements.txt

#### Testing

##### Requirements for tests

To run tests locally, you need to have MySQL v5.7 installed and database 'db_skale' and some tables created (see below). Also you have to change the name of `test_data/.env_template` to `test_data/.env` and fill it out with your environment variables:

    ETH_PRIVATE_KEY='YOUR_PRIVATE_KEY' 
    DB_ROOT_PASSWORD='YOUR_MYSQL_ROOT_PASSWORD'
    DB_USER='YOUR_MYSQL_USER'
    DB_PASSWORD='YOUR_MYSQL_PASSWORD'

As for using MySQL you have two options:

1.  Use MySQL docker container (recommended). In this case:
    \- install [Docker CE](https://docs.docker.com/install/) v18.06? (if you haven't it installed)
    \- run following command:

    docker run -d --restart=always --name skale-mysql -e MYSQL_ROOT_PASSWORD=$DB_ROOT_PASSWORD 
    \-e MYSQL_DATABASE=db_skale -e MYSQL_USER=$DB_USER -e MYSQL_PASSWORD=$DB_PASSWORD 
    \-v test_data/init.sql:/docker-entrypoint-initdb.d/init.sql -p 3307:3306  mysql/mysql-server:5.7

2.  If you already have MySQL v5.7 installed on your PC - create db named 'db_skale' and tables with a help of this [init.sql](https://github.com/skalenetwork/skale-nms/blob/develop/test_data/init.sql) file. Keep in mind that SLA agent uses MySQL on port 3307 (not 3306)

##### Run tests

    py.test -v tests/test_bounty.py

### Build and run

For building Bounty collector docker container and pushing it to Docker Hub use:

```bash
cd bounty
sh ./build.sh
```

Run docker container locally:

```bash
cd bounty
sh ./install.sh
```

## Build all containers

To build docker containers both for SLA agent and Bounty collector use:

```bash
sh ./build_all.sh
```

## Documentation

_in process_

## For more information

-   [SKALE Network Website](https://skale.network)
-   [SKALE Network Twitter](https://twitter.com/SkaleNetwork)
-   [SKALE Network Blog](https://skale.network/blog)

Learn more about the SKALE community over on [Discord](http://skale.chat).

## Contributing

**If you have any questions please ask our development community on [Discord](http://skale.chat).**

[![Discord](https://img.shields.io/discord/534485763354787851.svg)](https://discord.gg/vvUtWJB)

## License

[![License](https://img.shields.io/github/license/skalenetwork/skale-nms.svg)](LICENSE)

Copyright (C) 2018-present SKALE Labs
