FROM ubuntu:xenial
MAINTAINER Wei-Ning Huang <aitjcize@compose.ai>

RUN echo -n 'root:bb8root' | chpasswd

RUN apt-get update
RUN apt-get upgrade -y

RUN apt-get install -y vim git python2.7 python-pip nginx libpcre3-dev \
	libmysqlclient-dev  libjpeg-dev libpng-dev libsqlite3-dev \
	libncurses-dev supervisor openssh-server

RUN mkdir -p /var/run/apache2 /var/run/sshd /var/log/supervisor /var/tmp

# BB8 specific dependencies
ENV BB8_ROOT /srv/http/bb8

COPY requirements.txt /tmp/requirements.txt

# Install Python dependencies
RUN pip2 install --upgrade pip setuptools
RUN pip2 install -r /tmp/requirements.txt

# Install Configuration files
RUN echo 'daemon off;' >> /etc/nginx/nginx.conf
COPY conf/bb8.nginx.conf /etc/nginx/conf.d/bb8.nginx.conf
COPY conf/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Copy sources
RUN mkdir -p ${BB8_ROOT}
COPY . ${BB8_ROOT}

EXPOSE 22 5000
CMD ["/usr/bin/supervisord"]
