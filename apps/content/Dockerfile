FROM ubuntu:xenial
MAINTAINER Kevin Li <kevin@compose.ai>

RUN apt-get update && apt-get upgrade -y && \
        apt-get install -y vim git python python2.7 \
        python-pip libssl-dev libxml2-dev libxslt-dev \
        lib32z1-dev libffi-dev libssl-dev

COPY requirements.txt /tmp/requirements.txt

# Install Python dependencies
RUN pip2 install --upgrade pip setuptools
RUN pip2 install -r /tmp/requirements.txt

# Create required dir
RUN mkdir -p /opt/app /var/lib/crawler

# Install app script
COPY . /opt/app
COPY credential/compose-ai.json /opt/app

ENV GOOGLE_APPLICATION_CREDENTIALS=/opt/app/compose-ai.json
ENV DATABASE=mysql+pymysql://bb8:bb8test@172.17.0.1:3307/bb8?charset=utf8mb4

WORKDIR /opt/app
CMD ["./app.py"]
