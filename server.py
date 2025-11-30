import socket   
from threading import Thread
import os

BUFFER_SIZE = 4096      
ENC = 'utf-8'

class Server: 
    Clients = []

    def __init__(self, HOST, PORT):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((HOST, PORT))
        self.socket.listen(5)
        self.server_directory = './server_files'
        if not os.path.exists(self.server_directory):
            os.makedirs(self.server_directory)
        print(f"Server started on {HOST}:{PORT}")

    def listen(self):
        try:
            while True:
                client_socket, address = self.socket.accept()
                print(f"Connection with" + str(address) + " has been established.")

                client_name = client_socket.recv(1024).decode()
                client = {'client_name': client_name, 'client_socket': client_socket}

                self.broadcast_message(client_name, client_name + " has joined the chat.")
                self.Clients.append(client)
                Thread(target=self.handle_new_client, args=(client,)).start()
        except KeyboardInterrupt:
            print("Shutting down")
        finally:
            self.socket.close()

    def handle_new_client(self, client):
        client_socket = client['client_socket']
        client_name = client['client_name']

        while True:
            client_message = client_socket.recv(1024).decode()
            if client_message.strip() == client_name + ": bye" or not client_message.strip():
                self.broadcast_message(client_name, client_name + " has left the chat.")
                Server.Clients.remove(client)
                client_socket.close()
                break
            elif client_message.strip() == "/ls":
                files = [f for f in os.listdir(self.server_directory) if not f.startswith('.')]
                filelist = "\n".join(files) if files else "(no files)"
                client_socket.send(filelist.encode(ENC))
                continue
            elif client_message.startswith("/get"):
                _, filename, data_port_str = client_message.split(" ", 2)
                filename = filename.strip()
                data_port = int(data_port_str)


                filepath = os.path.join(self.server_directory, filename)

                data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                data_socket.connect(('localhost', data_port))

                if not os.path.exists(filepath) or not os.path.isfile(filepath):
                    data_socket.send("NOT_FOUND".encode(ENC))
                    data_socket.close()
                    continue

                filesize = os.path.getsize(filepath)
                data_socket.send(f"FOUND {filesize}".encode(ENC)) 


                with open(filepath, "rb") as f:
                    while True:
                        chunk = f.read(BUFFER_SIZE)
                        if not chunk:
                            break
                        data_socket.sendall(chunk)
                data_socket.close()
                print(f"Sent {filename} to {client_name} via data connection")
                continue
            elif client_message.startswith("/put"):
                parts = client_message.split(" ", 3)
                filename = parts[1]
                filesize = int(parts[2])
                data_port = int(parts[3])
                
                data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                data_socket.connect(('localhost', data_port))
                
                file_bytes = b''
                while len(file_bytes) < filesize:
                    chunk = data_socket.recv(min(BUFFER_SIZE, filesize - len(file_bytes)))
                    if not chunk:
                        break
                    file_bytes += chunk
                
                filepath = os.path.join(self.server_directory, filename)
                with open(filepath, "wb") as f:
                    f.write(file_bytes)
                
                data_socket.close()
                print(f"Received {filename} from {client_name} via data connection")
                continue
            else:
                self.broadcast_message(client_name, client_message)

    def broadcast_message(self, sender_name, message):
        for client in self.Clients:
            client_socket = client['client_socket']
            client_name = client['client_name']
            if client_name != sender_name:
                client_socket.send(f"CHAT:{message}".encode())


if __name__ == "__main__":
    server = Server('localhost', 12345)
    server.listen()