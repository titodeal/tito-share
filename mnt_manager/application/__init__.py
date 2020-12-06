import os
import sys
path = os.path.abspath("..")
sys.path.append(path)
from utils import user_util, cmd_util

from _sockets import socket_server
import traceback


class AplicationServer(socket_server.SocketServer):

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
                    traceback.print_exc()
                    exit_code = str(e)
            self.send_data(client, exit_code)
            print(f"=> End processing clinet: {peername}\n----------------")
