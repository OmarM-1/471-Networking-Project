import socket
from threading import Thread
import os
import time

BUFFER_SIZE = 4096
ENC = 'utf-8'
SERVER_IP = '52.53.179.251'
SERVER_PORT = 12345

class Client:

    def __init__(self, HOST, PORT):
        self.socket = socket.socket()
        self.socket.connect((HOST, PORT))
        self.socket.settimeout(0.1)
        self.server_ip = HOST
        
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
                self.socket.send(b"/ls")
                
                response = None
                start_time = time.time()
                while time.time() - start_time < 2:
                    try:
                        data = self.socket.recv(65536).decode(ENC)
                        if data and not data.startswith("CHAT:"):
                            response = data
                            break
                    except socket.timeout:
                        continue
                
                self.ftp_mode = False
                
                if response:
                    print("Files on server:\n" + response)
                else:
                    print("No response from server")
                    
                continue
                
            if client_input.startswith("/get "):
                # PASSIVE MODE: Client connects to server's data port
                _, filename = client_input.split(" ", 1)
                filename = filename.strip()

                # Request file from server
                self.socket.send(f"/get {filename}".encode(ENC))

                # Wait for server response with port number
                response = None
                for _ in range(50):
                    try:
                        response = self.socket.recv(1024).decode(ENC).strip()
                        if response and not response.startswith("CHAT:"):
                            break
                    except socket.timeout:
                        continue
                
                if not response:
                    print("No response from server")
                    continue
                
                if response == "NOT_FOUND":
                    print("Server: file not found.")
                    continue

                if response.startswith("FOUND "):
                    parts = response.split(" ")
                    filesize = int(parts[1])
                    data_port = int(parts[2])

                    # Connect to server's data port
                    try:
                        data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        data_socket.connect((self.server_ip, data_port))
                        
                        # Receive file
                        file_bytes = b''
                        while len(file_bytes) < filesize:
                            chunk = data_socket.recv(min(BUFFER_SIZE, filesize - len(file_bytes)))
                            if not chunk:
                                break
                            file_bytes += chunk
                        
                        data_socket.close()

                        # Save file
                        filepath = os.path.join(self.client_directory, filename)
                        with open(filepath, "wb") as f:
                            f.write(file_bytes)
                        print(f"Downloaded {filename} ({filesize} bytes) to {self.client_directory}/")
                    except Exception as e:
                        print(f"Error downloading file: {e}")
                        
                continue
                    
            if client_input.startswith("/put "):
                # PASSIVE MODE: Client connects to server's data port
                _, filename = client_input.split(" ", 1)
                filename = filename.strip()
                filepath = os.path.join(self.client_directory, filename)
                
                if not os.path.exists(filepath):
                    print(f"File '{filename}' not found in client directory.")
                    continue
                
                filesize = os.path.getsize(filepath)
                
                # Tell server we want to upload
                self.socket.send(f"/put {filename} {filesize}".encode(ENC))
                
                # Wait for server to tell us which port to connect to
                response = None
                for _ in range(50):
                    try:
                        response = self.socket.recv(1024).decode(ENC).strip()
                        if response and not response.startswith("CHAT:"):
                            break
                    except socket.timeout:
                        continue
                
                if not response or not response.startswith("READY "):
                    print("Server not ready for upload")
                    continue
                
                data_port = int(response.split(" ")[1])
                
                # Connect to server's data port
                try:
                    data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    data_socket.connect((self.server_ip, data_port))
                    
                    # Send file
                    with open(filepath, "rb") as f:
                        while True:
                            chunk = f.read(BUFFER_SIZE)
                            if not chunk:
                                break
                            data_socket.send(chunk)
                    
                    data_socket.close()
                    print(f"Uploaded {filename} ({filesize} bytes) to server")
                except Exception as e:
                    print(f"Error uploading file: {e}")
                    
                continue
                
            if client_input.startswith("/exit"):
                print("Exiting...")
                self.socket.close()
                os._exit(0)

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
    Client(SERVER_IP, SERVER_PORT)