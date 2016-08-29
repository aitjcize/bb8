FROM ubuntu:xenial
MAINTAINER Wei-Ning Huang <aitjcize@compose.ai>

RUN apt-get update && apt-get upgrade -y && \
	apt-get install -y vim git python2.7 python-pip nginx libpcre3-dev \
	libmysqlclient-dev libjpeg-dev libpng-dev libsqlite3-dev \
	libffi-dev libssl-dev libncurses-dev supervisor

COPY requirements.txt /tmp/requirements.txt

# Install Python dependencies
RUN pip2 install --upgrade pip setuptools
RUN pip2 install -r /tmp/requirements.txt

# Create log dirs
RUN mkdir -p /var/log/supervisor /var/log/bb8 /var/lib/bb8

# BB8 specific dependencies
ENV BB8_ROOT /opt/bb8

# Install Configuration files
COPY conf/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
RUN echo 'daemon off;' >> /etc/nginx/nginx.conf
COPY conf/bb8.nginx.conf /etc/nginx/conf.d/bb8.nginx.conf

# Environment variables
ENV BB8_DEPLOY=true
ENV PYTHONPATH=${BB8_ROOT}
ENV DATABASE=mysql+pymysql://bb8deploy:bb8deploymysql@/bb8?unix_socket=/cloudsql/dotted-lexicon-133523:asia-east1:bb8&charset=utf8mb4

# CloudSQL
RUN mkdir -p /cloudsql

VOLUME /var/log

EXPOSE 5000 62629
CMD ["/usr/bin/supervisord"]

# Copy sources
RUN mkdir -p ${BB8_ROOT}
COPY . ${BB8_ROOT}
