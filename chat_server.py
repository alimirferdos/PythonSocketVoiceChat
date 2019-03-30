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
        self.requests = []
        print("Server woke up! Let's wait for customers on " + str(self.ADDR))

    def accept_incoming_connections(self):
        """Sets up handling for incoming clients."""
        while True:
            client, client_address = self.socket.accept()
            print("%s:%s has connected." % client_address)
            client.send(bytes("SERVER: Greetings from the cave! Type your username and press enter!", "utf8"))
            self.clients.append(client)
            Thread(target=self.handle_client, args=(client,)).start()

    def handle_client(self, client):
        """Handles a single client connection."""
        name = client.recv(self.BUFFSIZE).decode("utf8")
        welcome = 'Welcome %s!' % name
        client.send(bytes(welcome, "utf8"))
        msg = "%s has joined the chat!" % name
        print(msg)
        self.client_names[name] = self.clients.index(client)
        while True:
            #print('waiting for command from client' , name)
            msg = pickle.loads(client.recv(self.BUFFSIZE))
            if type(msg) is dict:
                if msg['command'] == "get_clients":
                    self.send_client_list(client)
                elif msg['command'] == "disconnect":
                    # FIXME: when user exits this should happen!
                    #client.send(bytes("{quit}", "utf8")) => why?!
                    #del self.clients[client] => error : list indices must be integers or slices, not socket
                    del self.clients[self.client_names[name]]
                    del self.client_names[name] #delete username and indice
                    client.close()
                    print("%s has left the chat." % name)
                    break
                elif msg['command'] == "send_file":
                    print(name, 'wants send a file to', msg['receiver'])
                    self.requests.append({'sender' : name, 'receiver' : msg['receiver'], 'status' : 'pending'})
                    receiver_index = self.client_names[msg['receiver']]
                    if(name != msg['receiver']): #you can not send a file to yourself
                        self.send_file_request(name, msg['receiver'])
                    #print(self.client_names[msg['callee']])
                elif msg['command'] == 'answer':
                    sender = self.clients[self.client_names[msg['sender']]]
                    if(msg['value'] == 'yes'):
                        self.send(name+'has accepted the file', sender)
                    else:
                        self.send(name+'has rejected the file', sender)
            else:
                print(name + ": " + msg)

    def send_file_request(self, sender, receiver):
        receiver_index = self.client_names[receiver]
        msg = pickle.dumps({"command": "send_file", "sender": sender})
        self.send(msg, self.clients[receiver_index])
    def send_client_list(self, sock):
        sock.sendall(pickle.dumps(tuple(self.client_names.keys())))

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

    def send(self, msg, client):  # event is passed by binders.
        """Handles sending of messages."""
        if type(msg) is not bytes:
            client.send(bytes(msg, "utf8"))
        else:
            client.send(msg)
            #if msg == pickle.dumps({"command": "quite"}):
                #self.client_socket.close()
                #print("msg sent")

if __name__ == "__main__":
    SERVER = ChatServer()
    SERVER.run()
