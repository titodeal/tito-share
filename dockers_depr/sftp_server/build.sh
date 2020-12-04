#!/bin/bash

TAG="titodeal/sftp_server:0.0.1"
docker build . -t "$TAG" --network host

if [[ -n "$1" && -n "$2" && -n "$3" ]]; then
    echo $1 $2 $3
    volume="$3":/home/"$1"/mnt
    echo "volume is: $volume"
#     docker run -it -p 2222:22 --rm --volume "$volume" --name sftp_server_01 "$TAG" $1 $2
    docker run -d -p 2222:22 --rm --volume "$volume" --name sftp_"$1" "$TAG" $1 $2
else
    echo "required 'user', 'password' and 'volume' arguments" >&2
    exit 1
fi
# docker run -it -p 2222:22 --rm --name sftp_server_01 "$TAG" user1 passwd123
