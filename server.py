import socket   
from threading import Thread
import os
import random

BUFFER_SIZE = 4096      
ENC = 'utf-8'
# Define a port range for data connections (configure these in AWS Security Group)
DATA_PORT_MIN = 30000
DATA_PORT_MAX = 40000

class Server: 
    Clients = []

    def __init__(self, HOST, PORT):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((HOST, PORT))
        self.socket.listen(5)
        self.server_directory = './server_files'
        if not os.path.exists(self.server_directory):
            os.makedirs(self.server_directory)
        self.used_ports = set()
        print(f"Server started on {HOST}:{PORT}")
        print(f"Data port range: {DATA_PORT_MIN}-{DATA_PORT_MAX}")

    def get_data_port(self):
        """Get an available port in the configured range"""
        max_attempts = 100
        for _ in range(max_attempts):
            port = random.randint(DATA_PORT_MIN, DATA_PORT_MAX)
            if port not in self.used_ports:
                try:
                    # Test if port is available
                    test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    test_socket.bind(('', port))
                    test_socket.close()
                    self.used_ports.add(port)
                    return port
                except OSError:
                    continue
        raise Exception("No available ports in range")

    def release_port(self, port):
        """Release a port back to the pool"""
        self.used_ports.discard(port)

    def listen(self):
        try:
            while True:
                client_socket, address = self.socket.accept()
                print(f"Connection with {address} has been established.")

                client_name = client_socket.recv(1024).decode()
                client = {'client_name': client_name, 'client_socket': client_socket}

                self.broadcast_message(client_name, client_name + " has joined the chat.")
                self.Clients.append(client)
                Thread(target=self.handle_new_client, args=(client,)).start()
        except KeyboardInterrupt:
            print("\nShutting down")
        finally:
            self.socket.close()

    def handle_new_client(self, client):
        client_socket = client['client_socket']
        client_name = client['client_name']

        while True:
            try:
                client_message = client_socket.recv(1024).decode()
            except:
                self.broadcast_message(client_name, client_name + " has left the chat.")
                if client in Server.Clients:
                    Server.Clients.remove(client)
                client_socket.close()
                break
                
            if not client_message.strip():
                self.broadcast_message(client_name, client_name + " has left the chat.")
                if client in Server.Clients:
                    Server.Clients.remove(client)
                client_socket.close()
                break
                
            if client_message.strip() == "/ls":
                files = [f for f in os.listdir(self.server_directory) if not f.startswith('.')]
                filelist = "\n".join(files) if files else "(no files)"
                client_socket.send(filelist.encode(ENC))
                continue
                
            elif client_message.startswith("/get "):
                # PASSIVE MODE: Server creates listening socket and tells client the port
                _, filename = client_message.split(" ", 1)
                filename = filename.strip()
                
                filepath = os.path.join(self.server_directory, filename)
                
                if not os.path.exists(filepath) or not os.path.isfile(filepath):
                    client_socket.send("NOT_FOUND".encode(ENC))
                    continue
                
                filesize = os.path.getsize(filepath)
                
                # Get a port from our range
                try:
                    data_port = self.get_data_port()
                except Exception as e:
                    print(f"Error getting data port: {e}")
                    client_socket.send("ERROR".encode(ENC))
                    continue
                
                # Create data socket on the assigned port
                data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                data_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                data_socket.bind(('', data_port))
                data_socket.listen(1)
                data_socket.settimeout(30)  # 30 second timeout
                
                # Tell client the port and filesize
                client_socket.send(f"FOUND {filesize} {data_port}".encode(ENC))
                
                try:
                    # Wait for client to connect
                    conn, addr = data_socket.accept()
                    
                    # Send file
                    with open(filepath, "rb") as f:
                        while True:
                            chunk = f.read(BUFFER_SIZE)
                            if not chunk:
                                break
                            conn.sendall(chunk)
                    
                    conn.close()
                    print(f"Sent {filename} to {client_name} via data connection on port {data_port}")
                except socket.timeout:
                    print(f"Timeout waiting for client connection on port {data_port}")
                except Exception as e:
                    print(f"Error during file transfer: {e}")
                finally:
                    data_socket.close()
                    self.release_port(data_port)
                continue
                
            elif client_message.startswith("/put "):
                # PASSIVE MODE: Server creates listening socket and tells client the port
                parts = client_message.split(" ", 2)
                filename = parts[1]
                filesize = int(parts[2])
                
                # Get a port from our range
                try:
                    data_port = self.get_data_port()
                except Exception as e:
                    print(f"Error getting data port: {e}")
                    client_socket.send("ERROR".encode(ENC))
                    continue
                
                # Create data socket on the assigned port
                data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                data_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                data_socket.bind(('', data_port))
                data_socket.listen(1)
                data_socket.settimeout(30)  # 30 second timeout
                
                # Tell client we're ready and which port to connect to
                client_socket.send(f"READY {data_port}".encode(ENC))
                
                try:
                    # Wait for client to connect
                    conn, addr = data_socket.accept()
                    
                    # Receive file
                    file_bytes = b''
                    while len(file_bytes) < filesize:
                        chunk = conn.recv(min(BUFFER_SIZE, filesize - len(file_bytes)))
                        if not chunk:
                            break
                        file_bytes += chunk
                    
                    filepath = os.path.join(self.server_directory, filename)
                    with open(filepath, "wb") as f:
                        f.write(file_bytes)
                    
                    conn.close()
                    print(f"Received {filename} ({len(file_bytes)}/{filesize} bytes) from {client_name} via port {data_port}")
                except socket.timeout:
                    print(f"Timeout waiting for client connection on port {data_port}")
                except Exception as e:
                    print(f"Error during file transfer: {e}")
                finally:
                    data_socket.close()
                    self.release_port(data_port)
                continue
            else:
                self.broadcast_message(client_name, client_message)

    def broadcast_message(self, sender_name, message):
        for client in self.Clients:
            client_socket = client['client_socket']
            client_name = client['client_name']
            if client_name != sender_name:
                try:
                    client_socket.send(f"CHAT:{message}".encode())
                except:
                    pass


if __name__ == "__main__":
    server = Server('0.0.0.0', 12345)
    server.listen()