import os, sys
sys.path.append(os.path.abspath(".."))
sys.path.append(os.path.abspath("../.."))

from tito_sockets.application_server import ApplicationServer
from mnt_manager.mnt_manager_client import MountManager

import config as conf

from utils import user_util


class StorageServer(ApplicationServer):
    def __init__(self, port, timeout):
        super(StorageServer, self).__init__(port=port, timeout=timeout)

        self.mnt_manager = MountManager(conf.MNT_MANAGER_ADDRESS,
                               conf.MNT_MANAGER_PORT,
                               timeout=None)
        self.mnt_manager.set_connection()
        self.verified_connections = set()

    def handle_massage(self, msg, client):
        if msg.get("method") == "get_credentials":
            return self.get_credentials(client, *msg.get("args"))
        else:
            conn_valid_status = self.verify_connection(client)
            if not conn_valid_status[0]:
                return conn_valid_status
        print("TEST VERIFICATION FINISHED")
        method = getattr(self.mnt_manager, msg["method"])
        return method(*msg.get("args"))

    def get_credentials(self, client, user, passwd):
        user_exists = user_util.isuser_exists(user)
        if not user_exists[0]:
            return user_exists
        passwd_valid = user_util.check_userpasswd(user, passwd)
        if not passwd_valid[0]:
            return passwd_valid
        self.verified_connections.add((id(client), client.getpeername()))

    def verify_connection(self, client):
        if not(id(client), client.getpeername()) in self.verified_connections:
            answer = "=> Verification faild."
            return (False, answer)
        msg =  "=> Verification successfull."
        print(msg)
        return (True, msg)

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_type:
            print("!=> Exception occured: {}".format(exc_type))
        self._finish_server_process()
        self.mnt_manager.close_connection()


if __name__ == "__main__":
    with StorageServer(port=conf.PORT, timeout=0.05) as server:
        server.start_server()

# api = StorageServer(port=5055, timeout=0.05)
# api = api_client.Api(host=IP_SERVER, port=PORT_SERVER, timeout=1)
# api.mount_fs(MNT_FOLDER, "fed", "123", IP_SSH, PORT_SSH)
# api.umount_fs(MNT_FOLDER)
# api.share_catalog(f'/home/fed/projects', 'newuser_01', '123')
# api.share_catalog(f'/home/{OWNER}/newFolder', 'newuser_01', '123')
# api.close_connection()
