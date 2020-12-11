#!/usr/bin/python

from api.api_client import Api
from tito_sockets.application_server import ApplicationServer

IP_SSH = "192.168.88.163"
PORT_SSH = 22
MNT_FOLDER = "/home/new_user/folder/for_other"

IP_SERVER = "192.168.88.163"
PORT_SERVER = 50101


class Application(ApplicationServer):
    def __init__(self, port, timeout=0.2):
        super(Application, self).__init__(port=port, timeout=timeout)

        self.api = Api(IP_SERVER, PORT_SERVER, timeout=None)
        self.api.set_connection()

    def handle_massage(self, msg):
        method = getattr(self.api, msg.get("method"))
        return method(*msg.get("args"))

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_type:
            print("!=> Exception occured: {}".format(exc_type))
        self._finish_server_process()
        self.api.close_connection()


with Application(port=5055, timeout=0.05) as api:
    api.start_server()

# api = Application(port=5055, timeout=0.05)
# api = api_client.Api(host=IP_SERVER, port=PORT_SERVER, timeout=1)
# api.mount_fs(MNT_FOLDER, "fed", "123", IP_SSH, PORT_SSH)
# api.umount_fs(MNT_FOLDER)
# api.share_catalog(f'/home/fed/projects', 'newuser_01', '123')
# api.share_catalog(f'/home/{OWNER}/newFolder', 'newuser_01', '123')
# api.close_connection()
