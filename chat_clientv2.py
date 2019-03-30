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
        self.request_sent = False
        self.you_have_req = False
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sender = ""
    def run(self):
        self.client_socket.connect(self.ADDR)
        print("Connected!")
        receive_thread = Thread(target=self.receive)
        receive_thread.start()
        self.send(input()) #send username to server
        commands_thread = Thread(target=self.get_command)
        commands_thread.start()
        #self.get_client_list()

    def receive(self):
        """Handles receiving of messages."""
        while True:
            try:
                msg = self.client_socket.recv(self.BUFFSIZE)
                print(msg.decode("utf8"))
            except UnicodeDecodeError:
                msg = pickle.loads(msg)
                if(msg['command'] == 'send_file') :
                    if(self.you_have_req == False):
                        self.you_have_req = True
                        self.sender = msg['sender']
                        print(msg['sender'], 'wants send a file to you! Do you accept?! (yes/no)\n')
                    else:
                        print(msg['sender'], 'wants send a file to you! but you already have an unanswerd request')
            except OSError:  # Possibly client has left the chat.
                break

    def send(self, msg):  # event is passed by binders.
        """Handles sending of messages."""
        if type(msg) is not bytes:
            self.client_socket.send(bytes(msg, "utf8"))
        else:
            self.client_socket.send(msg)
            #if msg == pickle.dumps({"command": "quite"}):
                #self.client_socket.close()
                #print("msg sent")

    #@atexit.register
    def disconnect(self):
        """This function is to be called when the window is closed."""
        self.send(pickle.dumps({"command": "disconnect"}))
        self.client_socket.close()
        print('disconnected')
    def get_command(self):
        while True:
            if(self.request_sent):
                print('waiting for request answer!\n')
                while self.request_sent:
                    pass
            else:
                command = input('type command (send_file, disconnect, get_clients) : \n')
                if(command == 'send_file'):
                    receiver = input('type username of receiver : \n')
                    self.send_request(receiver)
                elif(command == 'disconnect'):
                    self.disconnect()
                    break
                elif (command == 'get_clients'):
                    self.get_client_list()
                elif (command == 'yes' or command =='no') and self.you_have_req:
                    self.send(pickle.dumps({"command": "answer", "value": command, 'sender': self.sender}))
                    self.you_have_req = False
                    if command == 'yes':
                        print('you have accepted the file\n')
                    else:
                        print('you have rejected')

    def get_client_list(self):
        self.send(pickle.dumps({"command": "get_clients"}))
        #Timer(1, self.get_client_list).start()

    def send_request(self, other_client):
        self.send(pickle.dumps({"command": "send_file", "receiver": other_client}))
        self.request_sent = True
        #self.wait_for_answer()
if __name__ == "__main__":
    CLIENT = ChatClient()
    CLIENT.run()
