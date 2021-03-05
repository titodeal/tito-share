import time

from tito_sockets import socket_client
from utils import user_util
from mnt_manager import methods_client


def benchmark(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        func(*args, *kwargs)
        print("***function name: {}\nduration: {}".format(func.__name__,
                                                          time.time() - start))
    return wrapper


class ServerError(Exception):
    pass


class MountManager(socket_client.SocketClient):
    def __init__(self, host, port, timeout=None):
        super(MountManager, self).__init__(host=host, port=port, timeout=timeout)

    def _send_reques(self, method_name, args):
        message = {"method": f"{method_name}", "args": args}
        self.send_data(message)
        response = self.recv_messages()
        print(f"=> Method process: '{method_name}' => Response is {response}")
        return response


#     @benchmark
    def mount_fs(self, mnt_folder, user_name, passwd, ip, port):

        print("=> Start moiunting fs")

        # Check the existance of the user
        user_exists, msg = user_util.isuser_exists(user_name)
        if not user_exists:
            err_msg = (f"!=>The '{user_name}' does not exits: ", msg)
            print(err_msg)
            return err_msg

        # Password user verification
        passwd_correct, msg = user_util.check_userpasswd(user_name, passwd)
        if not passwd_correct:
            err_msg = "!=> User verification failed: " + msg
            print(err_msg)
            return err_msg
        print("=>User verification successful")

        user = user_util.get_user_info(user_name)

        # Check the readiness of the mnt_folder
        mnt_folder_ready, msg = methods_client.check_mnt_folder(mnt_folder, user)
        if not mnt_folder_ready:
            print(msg)
            return msg
        print("=>The mount folder is ready")

        # Check the readiness of the ssh
        ssh_ready, msg = methods_client.ssh_ready(ip, port)
        if not ssh_ready:
            print(msg)
            return msg

        method_name = "mount_fs"
        args = [f"{mnt_folder}",
                f"{user_name}",
                f"{passwd}",
                f"{ip}",
                f"{port}"]
        return self._send_reques(method_name, args)

    def umount_fs(self, mnt_folder):
        method_name = "umount_fs"
        args = [f"{mnt_folder}"]
        return self._send_reques(method_name, args)

    def share_catalog(self, catalog, user, passwd):
        """append the share catalog for user docker container"""
        # Check the catalog is availalbe
        method_name = "share_catalog"
        args = [f"{catalog}", f"{user}", f"{passwd}"]
        return self._send_reques(method_name, args)
#         message = {"method": "share_catalog",
#                    "args": [f"{catalog}", f"{user}", f"{passwd}"]}

#         self.send_data(message)
#         response = self.recv_messages()
#         if response is not True:
#             self.close_connection()
#             raise ServerError('Error in server occured:\n{}'.format(response))
#         print("Answer is", response)

