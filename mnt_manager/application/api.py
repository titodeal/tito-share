# import time
import os
import subprocess
from subprocess import PIPE

from application import AplicationServer, sshfs_utils, user_util, cmd_util

# def benchmark(func):
#     def wrapper(*args, **kwargs):
#         start = time.time()
#         func(*args, *kwargs)
#         print("***Function name: {}\nDuration: {}"
#               "".format(func.__name__, time.time() - start))
#     return wrapper

class AplicationApi(AplicationServer):
    """The class which process client commands"""

    @staticmethod
    def mount_fs(mnt_folder, user_name, passwd, ip, port):
        """This method mount file system on the web server."""

        USER_HOMEPATH = os.path.join(user_util.get_home_path(), f"{user_name}")

        # Checking system user
        user_exists, msg = user_util.isuser_exists(user_name)
        if not user_exists:
            print(f"=>Start creating new user '{user_name}'")
            new_user, msg = user_util.create_user(user_name, passwd)
            if not new_user:
                err_msg = f"!=> Creating user '{user_name}' fail: " + msg
                print(err_msg)
                return(err_msg)
            else:
                print(f"=> Creating new user '{user_name}' have been succsessful")
        else:
            print(f"=> The user '{user_name}' already exists.")
            passwd_correct, msg = user_util.check_userpasswd(user_name, passwd)
            if not passwd_correct:
                err_msg = "!=> User verification failed: " + msg
                print(err_msg)
                return err_msg

        user = user_util.get_user_info(user_name)
        if not os.path.exists(USER_HOMEPATH):
            os.mkdir(USER_HOMEPATH, mode=0o751)
            os.chown(USER_HOMEPATH, user.get('uid'), user.get('gid'))

        # Prepare SSH setup
        sshfolder = "/".join([USER_HOMEPATH, ".ssh"])
        sshfs_utils.generate_sshkeys(sshfolder)

        mnt_point = "/".join([USER_HOMEPATH, "projects"])
        mount, msg = sshfs_utils.mount_sshfs(mnt_folder, mnt_point,
                                             user, passwd, ip, port)
        if not mount:
            err_msg = "!=>Mount error occured: " + msg
            print(err_msg)
            return err_msg

        print("=>Mount has been complete successful ", msg)
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
            msg = "Share error: {}".format(error.decode())
            print(msg)
            return(msg)
        else:
            msg = "Successful share"
            print(msg)

        return True
