FROM google/cloud-sdk
MAINTAINER Wei-Ning Huang <aitjcize@compose.ai>

RUN apt-get update && apt-get upgrade -y && \
        apt-get install -y vim git python python2.7 python-pip

# Dirs
RUN mkdir -p /var/lib/bb8/apps /opt/app

CMD ["/opt/app/sync_app_states.sh"]

# App
COPY . /opt/app
