FROM ubuntu:xenial
MAINTAINER Wei-Ning Huang <aitjcize@compose.ai>

RUN apt-get update && apt-get upgrade -y && \
        apt-get install -y vim git python python2.7 python-pip

COPY requirements.txt /tmp/requirements.txt

# Install Python dependencies
RUN pip2 install --upgrade pip setuptools
RUN pip2 install -r /tmp/requirements.txt

# Create required dir
RUN mkdir -p /opt/app /var/lib/youbike

EXPOSE 9999
CMD ["/opt/app/app.py"]

# Install app script
COPY . /opt/app
