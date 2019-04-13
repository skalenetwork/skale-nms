[![codecov](https://codecov.io/gh/skalenetwork/SLA/branch/develop/graph/badge.svg?token=aPCwLvSCAi)](https://codecov.io/gh/skalenetwork/SLA)

# sla-agent
Repo contains SLA agent and Bounty collector - parts of Skale node

### Project structure
SLA agent and Bounty collector use a common base class BaseAgent (dir agent).
Realizations of agents are located in 'sla' and 'bounty' directories respectively.  

### Usage
For building docker containers for all agents and pushing them to Docker Hub use:
```bash
sh ./build_all.sh
```