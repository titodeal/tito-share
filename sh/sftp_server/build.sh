#!/bin/bash

TAG="titodeal/sftp_server:0.0.1"
docker build sh/sftp_server -t "$TAG" --network host
# echo "PWD: " $(pwd)
if [[ -n "$1" && -n "$2" && -n "$3" ]]; then
    echo $1 $2 $3
    volume="$3":/home/"$1"/mnt
    echo "volume is: $volume"
    docker run -it -p 2222:22 --rm --volume "$volume" --name sftp_server_01 "$TAG" $1 $2
#     docker run -di -p 2222:22 --rm --volume "$volume" --name sftp_server_01 "$TAG" $1 $2
else
    echo "required 'user', 'password' and 'volume' arguments" >&2
    exit 1
fi
