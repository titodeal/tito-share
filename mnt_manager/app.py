#!/usr/bin/python3

from application import api

PORT = 50101
with api.AplicationApi(port=PORT, timeout=0.05, backlog=5) as api_server:
    api_server.start_server()
