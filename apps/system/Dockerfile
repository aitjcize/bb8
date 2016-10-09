FROM google/cloud-sdk
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

# Dirs
RUN mkdir -p /var/lib/bb8/apps /opt/app

CMD ["/opt/app/sync_app_states.sh"]

# App
COPY . /opt/app
