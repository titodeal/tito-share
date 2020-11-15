import socket
import json

class SocketClient():
    def __init__(self, family=socket.AF_INET, type_proto=socket.SOCK_STREAM,
                 host='localhost', port=9090, timeout=None):
        self.sock = socket.socket(family, type_proto)
        self.host = host
        self.port = port
        self.timeout = timeout 

#     def __exception_wrapper(func):
#         def wrapper(self, *args, **kwargs):
#             try:
#                 return func(self, *args, **kwargs)
#             except Exception as e:
#                 self.sock.close()
#                 raise
#         return wrapper
        
    def set_connection(self):
        self.sock.connect((self.host, self.port))
        self.sock.settimeout(self.timeout)
        print(self.sock.gettimeout(), "========================")

    def close_connection(self):
        self.send_data('CLOSECONNREQUEST')
        try:
            print("=> Closing connection: {}".format(self.sock.getsockname()))
            print(self.sock.close())
        except OSError:
            self.sock.close()

#     @__exception_wrapper 
    def send_data(self, data, last=False):
        print('=> Start sending data')

#         is_last = "<:IS_LAST:TRUE:>" if last else "<:IS_LAST:FALSE:>"

#         data = json.dumps(data) + is_last
#         data = data.encode()
        data = json.dumps(data).encode()
        data_size = len(data)
        try:
            head_datasize = data_size.to_bytes(2, "little")
            print('=> Data to send size is: ', data_size)
        except ConnectionResetError as e:
            print("Sending data error: ", e) 
            return

        sent_size = self.sock.send(head_datasize)
        print("Peer name is :", self.sock.getpeername())
        sent_data = self.sock.send(data)
        print("=> Finish sending data")

#     @__exception_wrapper
    def recv_messages(self, buffer_size=64):
        print("=> Start receiving messages")
#         messages = []
#         while True:
#             message, EOFrame = self.receive_data(buffer_size)
        message = self.receive_data(buffer_size)
#             if not message:
#                 break
#             messages.append(message)
#             if message:
#                 messages.append(message)
#                 if EOFrame == "<:IS_LAST:TRUE:>":
#                     break
#             else:
#                 break
        return message

    def receive_data(self, buffer_size):
        print("=> Checking receive data")
        try:
            head_datasize = int.from_bytes(self.sock.recv(2), 'little')
            print("=> Data to received size is: ", head_datasize)
        except (socket.timeout, BlockingIOError, ConnectionResetError) as e:
            print("=> Receive data error: ", e)
            return None
        except KeyboardInterrupt:
            print("=> Closing connection: {}". format(self.sock.getsockname()))
            self.sock.close()
            return None

        packets_count = int(head_datasize/buffer_size)
        if packets_count < 1:
            packets_count = 0
            tail_size = head_datasize
        else:
            tail_size = head_datasize % buffer_size

        received_data = b""
        for pack in range(packets_count):
            received_data += self.sock.recv(buffer_size)    
        received_data += self.sock.recv(tail_size)

        if not received_data:
            print("=> No data")
            return None

        if len(received_data) != head_datasize:
            print("--=> Error data transfer: the size does not mach")
            print("Size to recievd: {}, had received: {}".format(head_datasize, len(received_data)))
            raise ValueError("--=> Error data transfer: the size does not mach")

        print("=> Successful data transfer. Size is: ", len(received_data))
#         data = received_data.decode()
#         EOFrame = data[data.index('<:IS_LAST:'):]
#         message = data[:data.index('<:IS_LAST:')]
        message = json.loads(received_data.decode())
#         message = json.loads(message)
#         print('=> EOFrame ', EOFrame)
        print(' => Received Message is: ', message)
        return message
