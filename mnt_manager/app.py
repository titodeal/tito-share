#!/usr/bin/python3

from api import ApiServer 

PORT = 50101
with ApiServer(port=PORT, timeout=0.05, backlog=5) as api_server:
    api_server.start_server()

