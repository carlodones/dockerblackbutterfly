FROM resin/raspberry-pi3-debian:jessie

RUN apt-get update && apt-get install -yq \
   python3 python sense-hat raspberrypi-bootloader openssh-server dbus python-pip python3-pip apt-utils && \
   pip install MinimalModbus && \
   pip install modbus_tk && \
   pip install paho-mqtt && \
   pip install ntplib && \
   apt-get upgrade && \
   apt-get clean && rm -rf /var/lib/apt/lists/*

RUN mkdir /var/run/sshd \
    && echo 'root:resin' | chpasswd \
    && sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/' /etc/ssh/sshd_config \
    && sed -i 's/UsePAM yes/UsePAM no/' /etc/ssh/sshd_config

WORKDIR /usr/src/app

COPY . ./

ENV INITSYSTEM on

CMD ["./src/start.sh"]




