import socket   
from threading import Thread


class Server: 
    Clients = []

    def __init__(self, HOST, PORT):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # TCP socket to allow 5 connections maximum.
        self.socket.bind((HOST, PORT))
        self.socket.listen(5)
        print(f"Server started on {HOST}:{PORT}")


    def listen(self):
        while True:
            client_socket, address = self.socket.accept()
            print(f"Connection with" + str(address) + " has been established.")

            client_name = client_socket.recv(1024).decode()
            client = {'client_name': client_name, 'client_socket': client_socket}

            self.broadcast_message(client_name, client_name + " has joined the chat.")
            self.Clients.append(client)
            Thread(target = self.handle_new_client, args=(client,)).start()


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
                else:
                    self.broadcast_message(client_name, client_message)

    def broadcast_message(self, sender_name, message):
        for client in self.Clients:
            client_socket = client['client_socket']
            client_name = client['client_name']
            if client_name != sender_name:
                client_socket.send(message.encode())


if __name__ == "__main__":
    server = Server('localhost', 12345)
    server.listen()
