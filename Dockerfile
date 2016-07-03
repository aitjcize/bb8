FROM ubuntu:xenial
MAINTAINER Wei-Ning Huang <aitjcize@compose.ai>

RUN apt-get update
RUN apt-get upgrade -y

RUN apt-get install -y vim git python2.7 python-pip nginx libpcre3-dev \
	libmysqlclient-dev  libjpeg-dev libpng-dev libsqlite3-dev \
	libncurses-dev supervisor

COPY requirements.txt /tmp/requirements.txt

# Install Python dependencies
RUN pip2 install --upgrade pip setuptools
RUN pip2 install -r /tmp/requirements.txt

# Gather all logs
RUN mkdir -p /var/log/supervisor /var/log/bb8 /var/lib/bb8/third_party

# BB8 specific dependencies
ENV BB8_ROOT /srv/http/bb8

# Install Configuration files
COPY conf/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
RUN echo 'daemon off;' >> /etc/nginx/nginx.conf
COPY conf/bb8.nginx.conf /etc/nginx/conf.d/bb8.nginx.conf

# Copy sources
RUN mkdir -p ${BB8_ROOT}
COPY . ${BB8_ROOT}

# CloudSQL
RUN mkdir -p /cloudsql

VOLUME /var/log

EXPOSE 5000
CMD ["/usr/bin/supervisord"]
