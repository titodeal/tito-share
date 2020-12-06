import os
import subprocess
from subprocess import PIPE
import sys
path = os.path.abspath("..")
sys.path.append(path)
from utils import user_util, cmd_util


def check_mnt_folder(mnt_folder, user):

    mnt_folder = os.path.normpath(mnt_folder)
    if not (os.path.exists(mnt_folder) and os.path.isdir(mnt_folder)):
        print(f"!=> The folder does not exists or it is not a directory")

    if not path_check_access(mnt_folder):
        print(f"!=> The path '{mnt_folder}' not pass the test. ")
        return

    if not mntfolder_check_permission(mnt_folder, user):
        print(f"!=> The mnt_folder '{mnt_folder}' not pass the permission test. ")
        return

    return True

def mntfolder_check_permission(folder, user):
    fld_perm_cmd = f"stat {folder} --printf=%a"
    fld_uid_cmd = f"stat --printf=%u {folder}"
    fld_gname_cmd = f"stat --printf=%G {folder}"

    # Check the mount folder permission
    code, fld_perm, msg = cmd_util.run_subprocess(fld_perm_cmd)

    if code != 0:
        print("!=>Somting is wrong: ", msg)
        return

    if int(fld_perm[2]) > 0:
        print(f"The mount folder '{folder}' "
              "has too wide acces rights for other users. "
              "For full-fledged process it is recommended "
              "to set the rights to '770'")
        return

    if int(fld_perm[1]) < 7:
        print(f"The mount folder '{folder}' "
              f"has too limited acces rights ({fld_perm}). "
              "For full-fledged process it is recommended "
              "to set the rights to '770'")
        return

    code, fld_uid, msg = cmd_util.run_subprocess(fld_uid_cmd)
    code, fld_gname, msg = cmd_util.run_subprocess(fld_gname_cmd)

    if not (fld_uid == user.get("uid") or fld_gname in user.get('groups')):
        print(f"!=>The user '{user.get('name')}' has no access for mnt_folder '{folder}'. "
              f"Please add the '{user.get('name')}' to the group '{fld_gname}'.")
        return
    else:
        print(f"=>The user '{user.get('name')}' has all necessary permission")
        return True


def path_check_access(path):
    components = path.split(os.sep)
    for i in range(1, len(components) + 1):
        path = os.sep.join(components[:i])
        if not path:
            continue

        cmd = f"stat --printf=%a {path}"
        code, permission, msg = cmd_util.run_subprocess(cmd)
        if code != 0:
            print("!=>Checking rights error: ", msg)
            return

        if not (int(permission[1]) >= 1):
            print(f"!=>The folder '{path}' does not has access ({permission})."
                  "The recommended rights is: 710")
            return

    print("=>Checking path access is done successful.")
    return True

