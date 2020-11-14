#!/usr/bin/python

import os
import subprocess
from _lib import socketServer

PORT = 50101


class ApiServer(socketServer.SocketServer):
    def handle_clients(self):
        connections = self.get_connections()
        if not connections:
            return

        print("=> Connections count for process: ", len(connections))

        for idx, connection in enumerate(connections):
            client, addr = connection
            print(f"=> [{idx}] Start processing client: ",
                  client.getpeername())

            data = self.recv_messages(client, timeout=1)
            for msg in data:
                print('=> recieved message: ', msg)
                if isinstance(msg, dict) and "method" in msg:
                    if msg.get('method') in METHODS:
                        method = msg.get('method')
                        args = (msg.get('args'))
                        exit_code = METHODS.get(method)(*args)
                        self.send_data(client, exit_code, last=True)
#                         self.send_data(client, '__END_OF_MESSAGE__')
#             self.close_client(client)
            print("=> End processing clinet: ", addr)


def mount_fs(catalog, user, passwd, ip, port):

    print(" ======== muont method!")
#     return 0
    return 'Mnt complete!'
    try:
        subprocess.run(["grep", f"^{user}:", "/etc/passwd"],
                        check=True)

    except subprocess.CalledProcessError as err:
        print(f"Start creating user '{user}'")

        user_proc = subprocess.run(
            f"./create_user.sh {user} {passwd}", shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Creating user stdout: ",  user_proc.stdout)
        if user_proc.returncode != 0:
            print("Creating fail: ",  user_proc.stderr)
            return

        print(f"Creating user '{user}' succsessful")
    else:
        print(f"User '{user}' already exists.")

    if not os.path.exists(f"/home/{user}"):
        os.mkdir(f"/home/{use}", mode=0o770)
        
    basename = os.path.basename(catalog)
    mountpoint = f"/home/{user}/{basename}"
    home_catalog = f"/home/{user}"
    ssh_catalog = "/".join([home_catalog, ".ssh"])
    if not os.path.exists(ssh_catalog):
        os.mkdir(ssh_catalog, mode=0o750)
        key_file = "/".join([ssh_catalog, "id_rsa"])
        passphrase = "ComCliServPhrase"
#         cmd = f'./expect_sshkeygen "{passphrase}" "ssh-keygen -f {key_file}"'
        keygen_args = ["./expect_sshkeygen", f"{passphrase}", 
                       "ssh-keygen", "-f", f"{key_file}"]
#         keygen_proc = subprocess.run(cmd, shell=True)
        keygen_proc = subprocess.run(keygen_args)
#         sshkeygen_proc = subprocess.run("ssh-keygen", "-f", key_file)
        print("Keygen return code is: ", keygen_proc.returncode)
        

        if keygen_proc.returncode != 0:
            print("Keygen generating fail: ",  keygen_proc.stderr)
            return
        else:
            print("SSH keygen generated successfull")


    if not os.path.exists(mountpoint):
        import shutil
        os.mkdir(mountpoint)
        shutil.chown(mountpoint, user=user, group=user)

    print(f"Mount argumetns:\n \
user:{user},\n \
ip:{ip},\n \
port:{port},\n \
mountpoint:{mountpoint}\n")

#     sshfs_cmd = ["./expect_sshmount", f"{passwd}",
#                  "sshfs", "-oStrictHostKeyChecking=no",
#                  f"{user}@{ip}:{catalog}", f"{mountpoint}",
#                  "-p" f"{port}", "-o", "reconnect"]
    sshfs_cmd = ["sshfs", "-oStrictHostKeyChecking=no,password_stdin",
                 f"{user}@{ip}:{catalog}", f"{mountpoint}",
                 "-p", f"{port}"]
    print("command: ", sshfs_cmd)
    try:
        sshfs_mount = subprocess.Popen(sshfs_cmd, stdin=subprocess.PIPE)
        sshfs_mount.communicate(input=f"{passwd}".encode())
#         sshfs_mount = subprocess.run(sshfs_cmd)
#                                 stdout=subprocess.PIPE,
#                                 stderr=subprocess.PIPE)
#         
    except subprocess.CalledProcessError as err:
        print("Mounting Error: ", sshfs_mount.stderr)
    else:
        print("Mounting successful", sshfs_mount.stdout)

    return "MOUNT COMPLETE!"

def umount_fs(catalog):
    print(' ===== umaount method!')
    return 'Umnt complete!'
    cmd_umnt_point = f"mount -l -t fuse.sshfs | \
grep {catalog} | cut --delimiter=' ' --fields=3" 
    print("Umount cmd is: ", cmd_umnt_point)
    umnt_point_proc = subprocess.Popen(cmd_umnt_point,
        stdout=subprocess.PIPE, shell=True)
    umnt_point = umnt_point_proc.stdout.readline()
    umnt_point = umnt_point.decode().strip()
    print("Uount point is: ", umnt_point)

    umount_cmd = ["umount", f"{umnt_point}"]
    umount_proc = subprocess.run(umount_cmd)
    if umount_proc.returncode != 0:
        print(f"Error umount catalog: {catalog}") 
        return
    print(f"Umount catalog successful {catalog}")

    return "UNMOUNT COMPLETE!"

METHODS = {'mount_fs': mount_fs, 'umount_fs': umount_fs}

with ApiServer(port=PORT, timeout=1, backlog=1) as api_server:
    api_server.start_server()
# server = Server(port=PORT, timeout=1, backlog=1)
# server.start_server()

