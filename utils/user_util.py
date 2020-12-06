import subprocess
from subprocess import PIPE
from . import cmd_util
import platform


def get_home_path():
    if platform.system() == "Linux":
        return "/home"
    elif platform.system() == "Windows":
        return "C:\\Users"


def isuser_exists(user):
    """Check does the user exists in the system """
    proc = subprocess.run(f"grep '^{user}:' /etc/passwd",
                          shell=True, stdout=PIPE, stderr=PIPE)

    if proc.returncode != 0:
        return (False, proc.stderr.decode().strip())
    return (True, proc.stdout.decode().strip())


def create_user(user, passwd):
    """Creates system user"""
    print(f"=>Start creating user '{user}'")
    proc = subprocess.run(f"./sh/create_user.sh {user} {passwd}",
                          shell=True, stdout=PIPE, stderr=PIPE)

    if proc.returncode != 0:
        return (False, proc.stderr.decode().strip())
    return(True, proc.stdout.decode().strip())


def check_userpasswd(user, passwd):
    """Check user password"""

    cmd = f"grep '^{user}:' /etc/shadow | cut -d : -f 2 | cut -d $ -f 2"
    code, _id, err = cmd_util.run_subprocess(cmd)
    if not _id:
#         return(False, f"The user '{user}' not found")
        return(False, err)
    elif code != 0:
        return(False, err)

    cmd = f"grep '^{user}:' /etc/shadow | cut -d : -f 2 | cut -d $ -f 3"
    code, _salt, err = cmd_util.run_subprocess(cmd)
    if code != 0:
        return(False, err)

    cmd = f"grep '^{user}:' /etc/shadow | cut -d : -f 2 | cut -d $ -f 4"
    code, _hashed, err = cmd_util.run_subprocess(cmd)
    if code != 0:
        return(False, err)

    cmd = f"echo {passwd} | openssl passwd -{_id} -salt {_salt} -stdin | cut -d $ -f 4"
    code, _hash, err = cmd_util.run_subprocess(cmd)
    if code != 0:
        return(False, err)

    if _hashed != _hash:
        return(False, "Incorrect user password")
    return (True, "Password is correct")


# def get_uid(user):
#     uid_cmd = f'grep -E "^{user}:" /etc/passwd | cut -d : -f 3'
#     gid_cmd = f'grep -E "^{user}:" /etc/passwd | cut -d : -f 4'
#     code, uid, err = cmd_util.run_subprocess(uid_cmd)
#     code, gid, err = cmd_util.run_subprocess(gid_cmd)
#     return(uid, gid)

def get_user_info(user):

    uid_cmd = f'grep -E "^{user}:" /etc/passwd | cut -d : -f 3'
    gid_cmd = f'grep -E "^{user}:" /etc/passwd | cut -d : -f 4'
    home_cmd = f'grep -E "^{user}:" /etc/passwd | cut -d : -f 6'
    shell_cmd = f'grep -E "^{user}:" /etc/passwd | cut -d : -f 7'
    groups_cmd = f"groups {user} | cut -d : -f 2"

    code, uid, err = cmd_util.run_subprocess(uid_cmd)
    code, gid, err = cmd_util.run_subprocess(gid_cmd)
    code, home, err = cmd_util.run_subprocess(home_cmd)
    code, shell, err = cmd_util.run_subprocess(shell_cmd)
    code, groups, err = cmd_util.run_subprocess(groups_cmd)
    groups = groups.strip().split(" ")

    user_dict = {
                 "name": user,
                 "uid": int(uid),
                 "gid": int(gid),
                 "home": home,
                 "shell": shell,
                 "groups": groups
                 }

    return user_dict
#     return(uid, gid)
