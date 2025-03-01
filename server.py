import socket
import threading

# server configuration
HOST = "127.0.0.1"
PORT = 5005
clients = []

# handles new clients
def handle_client(client_socket, address):
    print(f"[NEW CONNECTION] {address} connected.")
    clients.append(client_socket)

    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break
            message = data.decode('utf-8')
            print(f"[{address}] {message}")
            broadcast(message, client_socket)
        except ConnectionResetError:
            break

    print(f"[DISCONNECTED] {address} disconnected.")
    clients.remove(client_socket)
    client_socket.close()

# Function to broadcast messages to all clients
def broadcast(message, sender_socket):
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message.encode('utf-8'))
            except:
                clients.remove(client)

# Start Server
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[SERVER STARTED] Listening on {HOST}:{PORT}")

    while True:
        client_socket, address = server.accept()
        thread = threading.Thread(target=handle_client, args=(
            client_socket, address), daemon=True)
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


if __name__ == "__main__":
    start_server()