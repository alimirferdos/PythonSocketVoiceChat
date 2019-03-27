import atexit
import pickle
import socket
from threading import Thread, Timer


class ChatClient:
    def __init__(self):
        host = input('Enter host: ')
        port = input('Enter port: ')
        if not host:
            self.HOST = "127.0.0.1"
        else:
            self.HOST = host
        if not port:
            self.PORT = 33000
        else:
            self.PORT = int(port)

        self.BUFFSIZE = 1024
        self.ADDR = (self.HOST, self.PORT)

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):
        self.client_socket.connect(self.ADDR)
        print("Connected!")
        receive_thread = Thread(target=self.receive)
        receive_thread.start()
        self.send(input())
        self.get_client_list()

    def receive(self):
        """Handles receiving of messages."""
        while True:
            try:
                msg = self.client_socket.recv(self.BUFFSIZE)
                print(msg.decode("utf8"))
            except UnicodeDecodeError:
                print(pickle.loads(msg))
            except OSError:  # Possibly client has left the chat.
                break

    def send(self, msg):  # event is passed by binders.
        """Handles sending of messages."""
        if type(msg) is not bytes:
            self.client_socket.send(bytes(msg, "utf8"))
        else:
            self.client_socket.send(msg)
            if msg == pickle.dumps({"command": "quite"}):
                self.client_socket.close()
                print("msg sent")

    @atexit.register
    def on_closing(self):
        """This function is to be called when the window is closed."""
        self.send(pickle.dumps({"command": "quite"}))

    def get_client_list(self):
        self.send(pickle.dumps({"command": "get_clients"}))
        self.call("Hossein")
        Timer(0.1, self.get_client_list).start()

    def call(self, other_client):
        self.send(pickle.dumps({"command": "call", "callee": other_client}))


if __name__ == "__main__":
    CLIENT = ChatClient()
    CLIENT.run()
