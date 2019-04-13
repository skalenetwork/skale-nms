# sla-agent
SLA agent runs on every node of Skale network, periodically gets a list of nodes to validate from SC,
checks its health metrics and sends transactions with average metrics to CS when it's time to send it

### Usage
For building docker container and pushing it to Docker Hub use:
```bash
sh ./build.sh
```
Run docker container:
```bash
sh ./install.sh
```
