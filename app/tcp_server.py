#!/usr/bin/python

import os
import subprocess
from subprocess import PIPE
from _lib import socketServer
import time

PORT = 50101

def benchmark(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        func(*args, *kwargs)
        print("***Function name: {}\nDuration: {}".format(func.__name__,
                                                          time.time() - start))
    return wrapper

class ApiServer(socketServer.SocketServer):

#     @benchmark
    def handle_clients(self):
        connections = self.get_connections()
        if not connections:
            return

        print("=> Connections count process: ", len(connections))

        for idx, client in enumerate(connections):
            peername = client.getpeername()
            print(f"[{idx}] Start processing client:\n{peername}")

            msg = self.recv_messages(client, timeout=0)
            if not msg:
                continue

            print('=> recieved message: ', msg)
            if not (isinstance(msg, dict) and "method" in msg):
                note = f'Message has wrong format\nMessege is: "{msg}"'
                print(note)
                exit_code = note
            else:
                try:
                    method = getattr(self, msg.get('method'))
                    exit_code = method(*msg.get('args'))
                except (AttributeError, TypeError) as e:
                    print(e.__repr__())
                    exit_code = e.__repr__()
            self.send_data(client, exit_code)

            print(f"=> End processing clinet: {peername}\n----------------")

    @staticmethod
    def mount_fs(catalog, user, passwd, ip, port):
        """This method mount file system on the web server."""

        # Check and process current user. If user not exists creates it.
        try:
            subprocess.run(["grep", f"^{user}:", "/etc/passwd"], check=True)
        except subprocess.CalledProcessError:
            print(f"=>Start creating user '{user}'")
            user_proc = subprocess.run(
                f"./sh/create_user.sh {user} {passwd}", shell=True,
                stdout=PIPE, stderr=PIPE)
            print("Creating user stdout: ",  user_proc.stdout.decode())
            if user_proc.returncode != 0:
                error_msg = f"Creating user '{user}' fail: " \
                                            + user_proc.stderr.decode()
                print('!=>', error_msg)
                return error_msg
            print(f"=> Creating user '{user}' succsessful")
        else:
            print(f"=> User '{user}' already exists.")
            
            _id = subprocess.run("grep '^{user}:' /etc/shadow | cut -d : -f 2 | cut -d $ -f 2", shell=True, stdout=PIPE).stdout.decode().strip()
            _salt = subprocess.run("grep '^{user}:' /etc/shadow | cut -d : -f 2 | cut -d $ -f 3", shell=True, stdout=PIPE).stdout.decode().strip()
            _hashed = subprocess.run("grep '^{user}:' /etc/shadow | cut -d : -f 2 | cut -d $ -f 4", shell=True, stdout=PIPE).stdout.decode().strip()

            _hash = subprocess.run(f"echo {passwd} | openssl passwd -{_id} -salt {_salt} -stdin | cut -d $ -f 4", shell=True, stdout=PIPE).stdout.decode().strip()
            print("=> Checking user password")
            if _hashed != _hash:
                err_msg = "!=> Incorect user password"
                print(err_msg)
                return err_msg

            
        uid_cmd = f'grep -E "^{user}:" /etc/passwd | cut -d : -f 3'
        pr_uid = subprocess.run(uid_cmd, shell=True, stdout=PIPE)
        if pr_uid.returncode != 0:
            print("!=> The user\'s '{user}' uid not found")
        else:
            uid = pr_uid.stdout.decode().strip()

        # Check and process home user path. If path not exists creates it.
        if not os.path.exists(f"/home/{user}"):
            os.mkdir(f"/home/{user}", mode=0o770)

        # Check and process ssh keys.
        basename = os.path.basename(catalog)
        mountpoint = f"/home/{user}/{basename}"
        home_catalog = f"/home/{user}"
        ssh_catalog = "/".join([home_catalog, ".ssh"])
        if not os.path.exists(ssh_catalog):
            os.mkdir(ssh_catalog, mode=0o750)
            key_file = "/".join([ssh_catalog, "id_rsa"])
            passphrase = "ComCliServPhrase"
            keygen_args = ["./sh/expect_sshkeygen", f"{passphrase}",
                           "ssh-keygen", "-f", f"{key_file}"]
            keygen_proc = subprocess.run(keygen_args)
            keygen_returncode = keygen_proc.returncode
            print("Keygen return code is: ", keygen_returncode)

            if keygen_returncode != 0:
                error_msg = "Keygen generating fail: " \
                                + keygen_proc.stderr
                print('!=>', error_msg)
                return error_msg
            else:
                print("=> SSH keygen generated successfull")

        if not os.path.exists(mountpoint):
            import shutil
            os.mkdir(mountpoint)
            shutil.chown(mountpoint, user=user, group=user)
            print(f"=> The mountpoint folder '{mountpoint}' has been created\n \
                    owner is: {user}")
            print(f"=> Owner ID is: {os.stat(mountpoint).st_uid}")


        print(f"Mount argumetns:\n \
    user:{user},\n \
    ip:{ip},\n \
    port:{port},\n \
    mountpoint:{mountpoint}\n")

    #     sshfs_cmd = ["./expect_sshmount", f"{passwd}",
    #                  "sshfs", "-oStrictHostKeyChecking=no",
    #                  f"{user}@{ip}:{catalog}", f"{mountpoint}",
    #                  "-p" f"{port}", "-o", "reconnect"]
        sshfs_cmd = ["sshfs", "-ononempty", "-oServerAliveCountMax=0", "-oallow_other", "-oStrictHostKeyChecking=no,password_stdin", f"-ouid={uid}", f"-ogid={uid}",
                     f"{user}@{ip}:{catalog}", f"{mountpoint}",
                     "-p", f"{port}"]
        print("command: ", sshfs_cmd)
        print(f"=> Owner ID is: {os.stat(mountpoint).st_uid}")
        try:
            sshfs_mount = subprocess.Popen(sshfs_cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            sshfs_mount.communicate(input=f"{passwd}".encode())
            outs, errs = sshfs_mount.communicate()
    #         sshfs_mount = subprocess.run(sshfs_cmd)
    #                                 stdout=PIPE,
    #                                 stderr=PIPE)
    #         
            if sshfs_mount.returncode != 0:
                print("Mounting Error: ", errs.decode())
                return errs.decode()
    #        print("RETURN CODE IS: ", sshfs_mount.returncode)
    #        print("Mounting Error: ", outs)
        except subprocess.CalledProcessError as err:
            print("Mounting Error: ", errs.decode())
        else:
            print("Mounting successful", outs.decode())

        print(f"=> Owner ID is: {os.stat(mountpoint).st_uid}")
        return True

    @staticmethod
    def umount_fs(catalog):

        cmd_umnt_point = f"mount -l -t fuse.sshfs | \
grep {catalog} | cut --delimiter=' ' --fields=3"
        print("Umount cmd is: ", cmd_umnt_point)
        umnt_point_proc = subprocess.Popen(cmd_umnt_point,
                                           stdout=PIPE, shell=True)
        umnt_point = umnt_point_proc.stdout.readline()

        if not umnt_point:
            error_msg = \
                "Error umount: Mount point '{}' not found."\
                .format(catalog)
            print(error_msg)
            return error_msg

        umnt_point = umnt_point.decode().strip()
        print("Umount point is: ", umnt_point)

        umount_cmd = ["umount", f"{umnt_point}"]
        umount_proc = subprocess.run(umount_cmd, stderr=PIPE)

        print(umount_cmd)
        if umount_proc.returncode != 0:
            error_msg = "Error umount: {} {} \
                        ".format(catalog, umount_proc.stderr)
            print('!=>', error_msg)
            return error_msg
        print(f"=> Umount catalog successful {catalog}")
        return True

    @staticmethod
    def share_catalog(catalog, user, passwd):
        """append the share catalog for user docker container"""
        args = ["./sh/sftp_server/build.sh", user, passwd, catalog]
        proc = subprocess.Popen(args, stdout=PIPE, stderr=PIPE)
        outputs, error =  proc.communicate()
        print("=========SHARE====================")
        print("output process: ", outputs.decode())
        print("error process: ", error.decode())

        if proc.returncode != 0:
            msg = "Share error: {}".format(proc.stderr)
            print(msg)
            return(msg)
        else:
            msg = "Successful share"
            print(msg)

        return True


with ApiServer(port=PORT, timeout=0.05, backlog=5) as api_server:
    api_server.start_server()

