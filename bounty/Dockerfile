FROM python:3.6.5

RUN mkdir /usr/src/bounty
RUN mkdir /usr/src/bounty/configs
WORKDIR /usr/src/bounty

COPY requirements.txt ./
RUN apt-get update && apt install -y libsecp256k1-dev
RUN pip install --no-cache-dir -r requirements.txt

COPY ./ .

CMD [ "python", "./agent.py" ]
