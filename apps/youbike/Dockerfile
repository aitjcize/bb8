FROM ubuntu:xenial
MAINTAINER Wei-Ning Huang <aitjcize@compose.ai>

RUN apt-get update && apt-get upgrade -y && \
        apt-get install -y --no-install-recommends apt-utils && \
        apt-get install -y \
                git \
                python \
                python2.7 \
                python-pip \
                python-pkg-resources \
                vim \
        && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt

# Install Python dependencies
RUN pip2 install --upgrade pip setuptools
RUN pip2 install -r /tmp/requirements.txt

# Create required dir
RUN mkdir -p /opt/app /var/lib/youbike

# Environment variables
ENV PYTHONPATH=/opt/app

EXPOSE 9999
CMD ["/opt/app/app.py"]

# Install app script
COPY . /opt/app
