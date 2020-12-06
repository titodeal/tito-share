#!/usr/bin/python

from api import api_client

IP_SSH = "192.168.88.163"
PORT_SSH = 22
MNT_FOLDER = "/home/new_user/folder/for_other"

IP_SERVER = "192.168.88.163"
PORT_SERVER = 50101

api = api_client.Api(host=IP_SERVER, port=PORT_SERVER, timeout=1)
api.mount_fs(MNT_FOLDER, "fed", "123", IP_SSH, PORT_SSH)
# api.umount_fs(CATALOGS)
# api.share_catalog(f'/home/fed/projects', 'newuser_01', '123')
# api.share_catalog(f'/home/{OWNER}/newFolder', 'newuser_01', '123')
api.close_connection()
