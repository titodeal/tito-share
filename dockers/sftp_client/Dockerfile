FROM debian:buster 
MAINTAINER Andriy Shell [titodeal]

RUN apt-get update && \
	apt-get install openssh-client -y && \
	apt-get install sshfs -y && \
	mkdir /mnt/sftp


COPY files/known_hosts /root/.ssh/
COPY files/entrypoint /
COPY files/keys/ /root/.ssh/

ENTRYPOINT ["/entrypoint"]
