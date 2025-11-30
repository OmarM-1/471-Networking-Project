import socket
from threading import Thread
import os
import time

BUFFER_SIZE = 4096
ENC = 'utf-8'

class Client:

    def __init__(self, HOST, PORT):
        self.socket = socket.socket()
        self.socket.connect((HOST, PORT))
        self.socket.settimeout(0.1) 
        
        self.name = input("Enter your name: ")       
        self.client_directory = './client_files'
        if not os.path.exists(self.client_directory):
            os.makedirs(self.client_directory)
        self.ftp_mode = False
        self.talk_to_server()

    def talk_to_server(self):
        self.socket.send(self.name.encode())
        Thread(target=self.receive_messages, daemon=True).start()
        self.send_message()

    def send_message(self):
        while True:
            client_input = input("")

            if client_input.startswith("/ls"):
                self.ftp_mode = True
                time.sleep(0.05) 
                self.socket.send(b"/ls")
                
                # Receive with retries
                response = None
                for _ in range(50):  # Try for up to 5 seconds
                    try:
                        response = self.socket.recv(65536).decode(ENC)
                        break
                    except socket.timeout:
                        continue
                
                if response:
                    print("Files on server:\n" + response)
                else:
                    print("No response from server")
                    
                self.ftp_mode = False
                continue
                
            if client_input.startswith("/get "):
                self.ftp_mode = True
                time.sleep(0.05) 
                _, filename = client_input.split(" ", 1)
                filename = filename.strip()
                self.socket.send(f"/get {filename}".encode(ENC))

    
                status = None
                for _ in range(50):
                    try:
                        status = self.socket.recv(1024).decode(ENC).strip()
                        break
                    except socket.timeout:
                        continue
                
                if not status:
                    print("No response from server")
                    self.ftp_mode = False
                    continue
                    
                if status == "NOT_FOUND":
                    print("Server: file not found.")
                    self.ftp_mode = False
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
                    
                self.ftp_mode = False
                continue
                    
            if client_input.startswith("/put "):

                _, filename = client_input.split(" ", 1)
                filename = filename.strip()
                filepath = os.path.join(self.client_directory, filename)
                
                if not os.path.exists(filepath):
                    print(f"File '{filename}' not found in client directory.")
                    continue
                
                filesize = os.path.getsize(filepath)
                self.socket.send(f"/put {filename} {filesize}".encode(ENC))
                
                data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                data_socket.bind(('localhost', 0))
                data_socket.listen(1)
                data_port = data_socket.getsockname()[1]
                
                self.socket.send(str(data_port).encode(ENC))
                
                conn, _ = data_socket.accept()
                
                with open(filepath, "rb") as f:
                    while True:
                        chunk = f.read(BUFFER_SIZE)
                        if not chunk:
                            break
                        conn.send(chunk)
                
                conn.close()
                data_socket.close()
                print(f"Uploaded {filename} ({filesize} bytes) to server")
                continue

            client_message = self.name + ": " + client_input
            self.socket.send(client_message.encode())

    def receive_messages(self):
        while True:
            if self.ftp_mode:
                time.sleep(0.01)
                continue
            
            try:
                server_message = self.socket.recv(1024).decode()
                if server_message and server_message.startswith("CHAT:"):
                    actual_message = server_message[5:]  
                    print("\033[1;31;40m" + actual_message + "\033[0m")
            except socket.timeout:
                continue  
            except Exception:
                os._exit(0)


if __name__ == "__main__":
    Client('localhost', 12345)