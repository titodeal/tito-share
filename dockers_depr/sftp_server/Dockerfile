FROM debian:buster

RUN apt-get update \
     && apt-get install openssh-server -y \
     && mkdir /run/sshd 
# RUN apt-get install vim -y

COPY files/sshd_config /etc/ssh/sshd_config
COPY files/entrypoint /entrypoint
COPY files/create_user.sh /usr/local/bin/
# COPY authorized_keys /home/ute/.ssh/authorized_keys

ENTRYPOINT ["/entrypoint"]
