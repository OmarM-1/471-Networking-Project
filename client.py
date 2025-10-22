import socket

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("localhost", 9999))
input_message = input("Enter message to send: ")
client.send(input_message.encode())
data = client.recv(1024)
print(f"Received from server: {data.decode()}") 
client.close()