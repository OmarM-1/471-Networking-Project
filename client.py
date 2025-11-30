import socket
from threading import Thread
import os

BUFFER_SIZE = 4096
ENC = 'utf-8'

class Client:

    def __init__(self, HOST, PORT):
        self.socket = socket.socket()
        self.socket.connect((HOST, PORT))
        self.name = input("Enter your name: ")
        self.talk_to_server()

        self.client_directory = './client_files'
        if not os.path.exists(self.client_directory):
            os.makedirs(self.client_directory)
    

    def talk_to_server(self):
        self.socket.send(self.name.encode())
        Thread(target=self.receive_messages).start()
        self.send_message()

    def send_message(self):
        while True:
            client_input = input("")

            if client_input.startswith("/ls"):
                self.socket.send(b"/ls")
                continue
            if client_input.startswith("/get "):
                _, filename = client_input.split(" ", 1)
                filename = filename.strip()
                self.socket.send(f"/get {filename}".encode(ENC))

                status = self.socket.recv(1024).decode(ENC).strip()
                if status == "NOT_FOUND":
                    print("Server: file not found.")
                    continue

                if status.startswith("FOUND "):
                    filesize = int(status.split(" ", 1)[1])

                    data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    data_socket.bind(('localhost', 0))  
                    data_socket.listen(1)
                    data_port = data_socket.getsockname()[1]

                    self.socket.send(str(data_port).encode(ENC))

                    conn, _ = data_socket.accept()

                    file_bytes = b''
                    while len(file_bytes) < filesize:
                        chunk = conn.recv(min(BUFFER_SIZE, filesize - len(file_bytes)))
                        if not chunk:
                            break
                        file_bytes += chunk
                    
                    conn.close()
                    data_socket.close()

                    filepath = os.path.join(self.client_directory, filename)
                    with open(filepath, "wb") as f:
                        f.write(file_bytes)
                    print(f"Downloaded {filename} ({filesize} bytes) to {self.client_directory}/")

                    continue
            if client_input.startswith("/put "):
                   continue 
                    

            client_message = self.name + ": " + client_input
            self.socket.send(client_message.encode())

    def receive_messages(self):
        while True:
            server_message = self.socket.recv(1024).decode()
            if not server_message.strip():
                os._exit(0)
            print("\033[1;31;40m" + server_message + "\033[0m")


if __name__ == "__main__":
    Client('localhost', 12345)
