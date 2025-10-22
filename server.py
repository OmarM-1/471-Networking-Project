import socket   

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('localhost', 9999))
server.listen(1)
print("TCP server up and listening on port 9999")

while True:
    conn, addr = server.accept()
    data = conn.recv(1024)
    print(f"Received message: {data.decode()} from {addr}")
    conn.send(data)

# Simple TCP Echo Server
# Listens on port 9999 and echoes back any received messages
# to the sender.
# To test, run client.py which sends a message to this server
# and prints the echoed response.
# To stop the server, interrupt the process (e.g., Ctrl+C).
# Note: This server runs indefinitely until manually stopped.
# Make sure to run client.py in a separate terminal or process.

