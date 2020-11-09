#!/bin/bash

TAG="titodeal/sftp_server:0.0.1"
docker build . -t "$TAG" --network host

docker run -it -p 2222:22 --rm --name sftp_server_01 "$TAG" user1 passwd123
