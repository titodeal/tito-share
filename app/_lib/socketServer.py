import socket
import json

# Socket serever
class SocketServer():
    def __init__(self, family=socket.AF_INET, type_proto=socket.SOCK_STREAM,
                 port=9090, backlog=5, timeout=None):
        self.sock = socket.socket(family, type_proto)
        self.port = port
        self.backlog = backlog
        self.connections = []
        self.timeout = timeout
        self.__book_port__()

    def __exception_wrapper(func):
        def wrapper(self, *args, **kwargs):
            try:
                func(self, *args, **kwargs)
            except Exception:
                self.sock.close()
                for client, addr in self.connections:
                    print("= Closing client socket: ", addr)
                    client.close()
                print("=> Closing server socket")
                raise
        return wrapper

    def __book_port__(self):
        print(f"=> Binding '{self.port}' port")
        self.sock.bind(('', self.port))
        print(f"=> Port '{self.port}' booked successfully")
        self.sock.listen(self.backlog)
        self.sock.settimeout(self.timeout)

    @__exception_wrapper
    def start_server(self):
        print("=> Start listening")
        while True:
            try:
                self.connections.append(self.sock.accept())
            except KeyboardInterrupt:
                self.sock.close()
                break
            except socket.timeout:
                self.handle_clients()
                self._clean_failure()
            else:
                pass

    def _clean_failure(self):
        updated_connections = []
        for connection in self.connections:
            client = connection[0]
            if not client.fileno() == -1:
                updated_connections.append(connection)
        self.connections = updated_connections

    @__exception_wrapper
    def handle_clients(self):
        raise KeyboardInterrupt

    def get_connections(self):
        return self.connections

#     def get_data(self, client, buffer_size=64):
#         return self.get_messages(client, buffer_size

    def close_client(self, client):
        try:
            print("=> Closing socket: {}".format(client.getpeername()))
            client.close()
        except OSError:
            client.close()

    def recv_messages(self, client, buffer_size=64, timeout=None):
        print("=> Start receiving messages")
        client.settimeout(timeout)
        messages = []
        while True:
            data = self.receive_data(client, buffer_size)
            if not data:
                break
            messages.append(data)
        return messages

    def receive_data(self, client, buffer_size):
        print("=> Cecking receive data")
        try:
            head_datasize = int.from_bytes(client.recv(2), 'little')
            print("=> Data to received size is: ", head_datasize)
        except (socket.timeout, BlockingIOError):
            return

        packets_count = int(head_datasize/buffer_size)
        if packets_count == 0:
            tail_size = head_datasize
        else:
            tail_size = head_datasize % buffer_size
#         if packets_count < 1:
#             packets_count = 0
#             tail_size = head_datasize
#         else:
#             tail_size = head_datasize % buffer_size

        received_data = b""
        for pack in range(packets_count):
            received_data += client.recv(buffer_size)
        received_data += client.recv(tail_size)

        if not received_data:
            print("=> No data")
            return

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

        data = json.dumps(data).encode()
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

    def fs_mount(self):
        print("=> mounting")

    def fs_unmount(sefl):

        print("=> umounting")
