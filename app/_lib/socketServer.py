import socket
import json


class SocketServer():
    def __init__(self, family=socket.AF_INET, type_proto=socket.SOCK_STREAM,
                 port=9090, backlog=5, timeout=None):
        self.sock = socket.socket(family, type_proto)
        self.port = port
        self.backlog = backlog
        self.connections = []
        self.timeout = timeout
        self._book_port()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tracebach):
        if exc_type:
            print('=> Exceptioin occured: {}'.format(exc_type))
        self._finish_server_proces()

    def _finish_server_proces(self):
        for client  in self.connections:
            print("= Closing client socket: ", client.getpeername())
            client.close()
        print("=> Closing server socket")
        self.sock.close()

    def _clean_failure(self):
        updated_connections = []
        for client in self.connections:
            if not client.fileno() == -1:
                updated_connections.append(client)
        self.connections = updated_connections

    def _book_port(self):
        print(f"=> Binding '{self.port}' port")
        self.sock.bind(('', self.port))
        print(f"=> Port '{self.port}' booked successfully")
        self.sock.listen(self.backlog)
        self.sock.settimeout(self.timeout)
#         self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

    def start_server(self):
        print("=> Start listening")
        while True:
            try:
                self.connections.append(self.sock.accept()[0])
            except KeyboardInterrupt:
                break
            except (socket.timeout, BlockingIOError):
                self.handle_clients()
                self._clean_failure()
            else:
                pass

    def handle_clients(self):
        raise NotImplementedError

    def get_connections(self):
        return self.connections

    def close_client(self, client):
        try:
            self.connections.pop(self.connections.index(client))
        except ValueError:
            print('=> Client {} not found in connections list'.format(client.getpeername()))

        try:
            print("=> Closing socket: {}".format(client.getpeername()))
            client.close()
        except OSError:
            client.close()

    def recv_messages(self, client, buffer_size=64, timeout=None):
        print("=> Start receiving messages")
        client.settimeout(timeout)

        message = self.receive_data(client, buffer_size)
        if message == "CLOSECONNREQUEST":
            self.close_client(client)
            return
        return message

    def receive_data(self, client, buffer_size):
        print("=> Checking receive data")
        try:
            head_datasize = int.from_bytes(client.recv(2), 'little')
            print("=> Data to received size is: ", head_datasize)
        except (socket.timeout, BlockingIOError) as e:
            return None

        packets_count = int(head_datasize/buffer_size)
        if packets_count == 0:
            tail_size = head_datasize
        else:
            tail_size = head_datasize % buffer_size

        received_data = b""
        for pack in range(packets_count):
            received_data += client.recv(buffer_size)
        received_data += client.recv(tail_size)

        if not received_data:
            print("=> No data")
            return None

        if len(received_data) != head_datasize:
            print("--=> Error data transfer: the size does not mach")
            print("Size to recievd: {}, had received: {}".format(head_datasize,
                  len(received_data)))
            raise ValueError("--=> Error data transfer: the size does not mach")

        print("=> Successful data transfer. Size is: ", len(received_data))
        message = json.loads(received_data.decode())
        return message

    def send_data(self, client, data):
        print('=> Start sending data')
        print('Data = ', data)

        data = json.dumps(data)
        data = data.encode()
        data_size = len(data)
        head_datasize = data_size.to_bytes(2, "little")
        print('=> Data to send size is: ', data_size)

        try:
            sent_size = client.send(head_datasize)
            sent_data = client.send(data)
        except BrokenPipeError:
            print(f"Connection client was lost: {client}")
            return
        else:
            print("=> Finish sending data")
