#!/usr/bin/python

import sys
import os
import time
import subprocess
from subprocess import PIPE
import json

import sys
path = os.path.abspath("..")
sys.path.append(path)

from _sockets import socket_client
from utils import user_util
from api import methods_client

# is openssh exists.
# check openssh config.
# chkeck outside ip channel.
# username - login (db).




# password random generte.
# ip and port (config). 
# main folders (config).


def benchmark(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        func(*args, *kwargs)
        print("***function name: {}\nduration: {}".format(func.__name__,
                                                          time.time() - start))
    return wrapper

class ServerError(BaseException):
    pass


class Api:
    def __init__(self, host, port, timeout=None):
        self.connection = socket_client.SocketClient(host=host,
                                                    port=port,
                                                    timeout=timeout)
        self.connection.set_connection()

    def close_connection(self):
        self.connection.close_connection()

    @benchmark
    def umount_fs(self, mnt_folder):

        message = {"method": "umount_fs",
                   "args": [f"{mnt_folder}"]}
        self.connection.send_data(message)
        answer = self.connection.recv_messages()
        if answer is not True:
            self.close_connection()
            raise ServerError('Error in server occured:\n{}'.format(answer))
        print("Answer is", answer)

    def __enter__(self):
        return self

    def __exit__(self):
        self.close_connection()

#     @benchmark
    def mount_fs(self, mnt_folder, user_name, passwd, ip, port):

        # Check the existance of the user
        user_exists, msg = user_util.isuser_exists(user_name)
        if not user_exists:
            print(f"!=>The '{user_name}' does not exits: ", msg)
            return

        # Password user verification
        passwd_correct, msg = user_util.check_userpasswd(user_name, passwd)
        if not passwd_correct:
            err_msg = "!=> User verification failed: " + msg
            print(err_msg)
            return
        print("=>User verification successful")

        user = user_util.get_user_info(user_name)

        # Check the readiness of the mnt_folder
        if not methods_client.check_mnt_folder(mnt_folder, user):
            return
        print("=>The mount folder is ready")

        # Check the readiness of the ssh
        if not ssh_ready(ip, port):
            return

        message = {"method": "mount_fs",
                   "args": [f"{mnt_folder}", f"{user_name}", f"{passwd}",
                            f"{ip}", f"{port}"]}

        self.connection.send_data(message)
        answer = self.connection.recv_messages()
        if answer is not True:
            self.close_connection()
            raise ServerError( answer)
        print("Answer is", answer)


    def share_catalog(self, catalog, user, passwd):
        """append the share catalog for user docker container"""
        # Check the catalog is availalbe
        message = {"method": "share_catalog",
                   "args": [f"{catalog}", f"{user}", f"{passwd}"]}

        self.connection.send_data(message)
        answer = self.connection.recv_messages()
        if answer is not True:
            self.close_connection()
            raise ServerError('Error in server occured:\n{}'.format(answer))
        print("Answer is", answer)

# def permission_ready(catalog, user):
# 
#     if not os.path.exists(catalog):
#         print(f"Path is not exists: {catalog}")
#         return
# 
#     try:
#         subprocess.run(["grep", f"^{user}:", "/etc/passwd"], check=True)
#     except subprocess.CalledProcessError as err:
#         print(f"User {user} not exists")
#         return
# 
# #     try:
# #         chedk read/write perm
# 
#     try:
#        cmd = f"groups {user} | grep -w $(stat -c %G '{catalog}')"
#        subprocess.run(cmd, shell=True, check = True)
#     except:
#         print(f"The user '{user}' not include in catalog group. have no permission for {catalog}")
#         return
# 
#     cmd = f"stat --printf=%a {catalog}  | cut -c 2"
#     proc_prm =  subprocess.run(cmd, shell=True, stdout=PIPE)
#     grp_perm = proc_prm.stdout
#     if grp_perm != 7:
#         print(f"Catalog group has insufficient permissions: {catalog}")
# 
#     return True

def ssh_ready(ip, port):
    try:
        ssh = subprocess.run(["ssh", "-V"], check=True)
        print("=> SSH package is found")
    except subprocess.CalledProcessError as err:
        print("=> SSH package not found.")
        return False

    try:
        ssh_port = subprocess.run(["nc","-z", ip,
                                   str(port)], check=True)
    except subprocess.CalledProcessError as err:
        print(f"!=>No SSH server at the addres: {IP_STORAGE}:{PORT_STORAGE}")
        return False

    return True

def config_ready():
    pass
