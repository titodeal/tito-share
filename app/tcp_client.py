#!/usr/bin/python

import sys
import os
import time
import subprocess
import json

from _lib import socketClient

# is Openssh exists.
# check Openssh config.
# chkeck outside ip channel.
# username - login (db).




# password random generte.
# ip and port (config). 
# main folders (config).

CATALOGS = ["/home/Development/titoshare/app/prod_projects/Prj3",
            "/home/Development/titoshare/app/prod_projects/Prj2"]

CATALOGS = "/home/fed/Development/titoshare/app/prod_projects"

# IP_STORAGE = "178.150.59.84"
# PORT_STORAGE = 2222
IP_STORAGE = "192.168.88.202"
PORT_STORAGE = 22
OWNER = "utes"

# IP_SERVER = "178.150.59.84" # "localhost"
# IP_SERVER = "192.168.88.202"
IP_SERVER = "192.168.88.174"
PORT_SERVER = 50101
    
class Api:
    def __init__(self):
        self.connection = socketClient.SocketClient(host=IP_SERVER,
                                                    port=PORT_SERVER,
                                                    timeout=None)

    def umount_fs(self, catalog):

        message = {"method": "umount_fs",
                   "args": [f"{catalog}"]}
        self.connection.set_connection()
        self.connection.send_data(message)
        answer = self.connection.recv_messages()
        print("Answer is", answer)
        self.connection.close_connection()
        
    def mount_fs(self, catalog, owner, passwd, ip, port):
        if not ssh_ready():
            return

        if not permission_ready(CATALOGS, OWNER):
            return
  
        message = {"method": "mount_fs",
                   "args": [f"{catalog}", f"{owner}", f"{passwd}",
                            f"{ip}", f"{port}"]}

        self.connection.set_connection()
        self.connection.send_data(message)
        answer = self.connection.recv_messages()
        print("Answer is", answer)
        self.connection.close_connection()


def permission_ready(catalog, user):

    if not os.path.exists(catalog):
        print(f"Path is not exists: {catalog}")
        return

    try:
        subprocess.run(["grep", f"^{user}:", "/etc/passwd"], check=True)
    except subprocess.CalledProcessError as err:
        print(f"User {user} not exists")
        return

#     try:
#         chedk read/write perm

    try:
       cmd = f"groups {user} | grep -w $(stat -c %G '{catalog}')"
       subprocess.run(cmd, shell=True, check = True)
    except:
        print(f"The user '{user}' not include in catalog group. have no permission for {catalog}")
        return

    cmd = f"stat --printf=%a {catalog}  | cut -c 2"
    proc_prm =  subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
    grp_perm = proc_prm.stdout
    if grp_perm != 7:
        print(f"Catalog group has insufficient permissions: {catalog}")

    return True

    
def ssh_ready():
    try:
        ssh = subprocess.run(["ssh", "-V"], check=True)
        print("=> SSH package is found")
    except subprocess.CalledProcessError as err:
        print("=> SSH package not found.")
        return False

    try:
        ssh_port = subprocess.run(["nc","-z", IP_STORAGE,
                                   str(PORT_STORAGE)], check=True)
    except subprocess.CalledProcessError as err:
        print(f"No SSH server at the addres: {IP_STORAGE}:{PORT_STORAGE}")
        return False

    return True

def config_ready():
    pass

# api = Api()
# api.mount_fs(CATALOGS, OWNER, "321", IP_STORAGE, PORT_STORAGE)
api = Api()
api.umount_fs(CATALOGS)

