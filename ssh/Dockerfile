FROM resin/%%RESIN_MACHINE_NAME%%-debian

RUN apt-get update && apt-get install -yq --no-install-recommends \
    openssh-server && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN mkdir /var/run/sshd \
    && echo 'root:resin' | chpasswd \
    && sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/' /etc/ssh/sshd_config \
    && sed -i 's/UsePAM yes/UsePAM no/' /etc/ssh/sshd_config

WORKDIR /usr/src/app

COPY . ./

ENV INITSYSTEM on

CMD ["./src/start.sh"]





#FROM resin/raspberry-pi3-debian:jessie
#FROM resin/raspberrypi3-python:latest