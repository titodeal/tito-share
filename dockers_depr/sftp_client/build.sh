#!/bin/bash

TAG=titodeal/sftp_client:0.0.1

# docker image rm -f $TAG

docker build . -t $TAG --network host 
docker run -it --rm --network=host --name sftp_client_01 --cap-add SYS_ADMIN --device=/dev/fuse $TAG 123 arg2 arg3
