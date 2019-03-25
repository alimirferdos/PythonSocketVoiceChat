import pickle
import socket
from threading import Thread


class ChatServer:
    def __init__(self):
        self.clients = []
        self.client_names = {}
        self.HOST = 'localhost'
        self.PORT = 33000
        self.BUFFSIZE = 1024
        self.ADDR = (self.HOST, self.PORT)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.socket.bind(self.ADDR)
        self.socket.listen(5)
        self.ADDR = self.socket.getsockname()
        print("Server woke up! Let's wait for customers on " + str(self.ADDR))

    def accept_incoming_connections(self):
        """Sets up handling for incoming clients."""
        while True:
            client, client_address = self.socket.accept()
            print("%s:%s has connected." % client_address)
            client.send(bytes("SERVER: Greetings from the cave! Type your username and press enter!", "utf8"))
            self.clients.append(client_address)
            Thread(target=self.handle_client, args=(client,)).start()

    def handle_client(self, client):
        """Handles a single client connection."""

        name = client.recv(self.BUFFSIZE).decode("utf8")
        welcome = 'Welcome %s!' % name
        client.send(bytes(welcome, "utf8"))
        msg = "%s has joined the chat!" % name
        print(msg)
        self.client_names[client] = name

        while True:
            msg = client.recv(self.BUFFSIZE)
            if msg == bytes("get_clients", "utf8"):
                self.send_client_list(client)
            elif msg != bytes("{quit}", "utf8"):
                print(name + ": " + msg)
            else:
                # FIXME: when user exits this should happen!
                client.send(bytes("{quit}", "utf8"))
                client.close()
                del self.clients[client]
                print("%s has left the chat." % name)
                break

    def send_client_list(self, sock):
        sock.sendall(pickle.dumps(tuple(self.client_names.values())))

    def broadcast(self, msg, prefix=""):  # prefix is for name identification.
        """Broadcasts a message to all the clients."""

        for sock in self.clients:
            try:
                sock.send(bytes(prefix, "utf8") + msg)
            except:
                pass

    def run(self):
        accept_thread = Thread(target=self.accept_incoming_connections)
        accept_thread.start()
        accept_thread.join()
        self.socket.close()


if __name__ == "__main__":
    SERVER = ChatServer()
    SERVER.run()
