import os
import subprocess
from subprocess import PIPE


def check_sshkeys(sshfolder):
    pass


def generate_sshkeys(sshfolder):
    """docstring for fnamegetnerate_sshkesy"""

    if not os.path.exists(sshfolder):
        os.mkdir(sshfolder, mode=0o750)
        key_file = "/".join([sshfolder, "id_rsa"])
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


def mount_sshfs(mnt_folder, mnt_point, user, passwd, ip, port):
    """docstrinfnameg for mount_sshfs"""

    print(user)
    user_name = user.get('name')
    uid = user.get('uid')
    gid = user.get('gid')

    print(f"Mount argumetns:\n \
    user:{user_name},\n \
    ip:{ip},\n \
    port:{port},\n \
    mnt_point:{mnt_point}\n \
    mnt_folder:{mnt_folder}\n")

#     catalog_name = os.path.catalog_name(catalog)
#     mnt_point = f"/home/{user}/{catalog_name}"
    if not os.path.exists(mnt_point):
        os.mkdir(mnt_point, mode=0o750)
        os.chown(mnt_point, uid, gid)
        print(f"=> The mountpoint folder '{mnt_point}'"
              f" has been created\n owner is: {user_name}")

#                  "-oServerAliveCountMax=0", "-oallow_other", "-oreconnect",
    sshfs_cmd = ["sshfs",
                 "-oallow_other", "-oreconnect",
                 "-oStrictHostKeyChecking=no,password_stdin",
                 f"-ouid={uid}", f"-ogid={gid}",
                 f"{user_name}@{ip}:{mnt_folder}", f"{mnt_point}", "-p", f"{port}"]

    print("sshfs command is: ", sshfs_cmd)

    sshfs_mount = subprocess.Popen(sshfs_cmd, stdin=PIPE,
                                   stdout=PIPE, stderr=PIPE)

    sshfs_mount.communicate(input=f"{passwd}".encode())
    outs, errs = sshfs_mount.communicate()

    if sshfs_mount.returncode != 0:
        print("!=>Mount error occured: ", errs.decode())
        return False, errs.strip().decode()
#     print("=>Mount has been complete successful", outs.decode())

    return True, outs.strip().decode()


