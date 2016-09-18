FROM ubuntu:xenial
MAINTAINER Kevin Li <kevin@compose.ai>

RUN apt-get update && apt-get upgrade -y && \
        apt-get install -y vim git python python2.7 \
        python-pip libssl-dev libxml2-dev libxslt-dev \
        lib32z1-dev libffi-dev libssl-dev supervisor

COPY requirements.txt /tmp/requirements.txt

# Install Python dependencies
RUN pip2 install --upgrade pip setuptools
RUN pip2 install -r /tmp/requirements.txt

# Create required dir
RUN mkdir -p /opt/app /var/log/supervisor

# Install configurations
COPY conf/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# CloudSQL
RUN mkdir -p /cloudsql

# Environment variables
ENV PYTHONPATH=/opt/app

EXPOSE 9999
CMD ["/usr/bin/supervisord"]

# Install app script
COPY . /opt/app

# Install client package
RUN pip install /opt/app/bb8-client-9999.tar.gz
