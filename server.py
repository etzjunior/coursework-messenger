import socket
import threading

clients = {}


def handle_client(client_socket, username):
    """Handles receiving and broadcasting messages for a client."""
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if not message:
                break

            broadcast(f"{username}: {message}", client_socket)
        except:
            break

    del clients[username]
    client_socket.close()


def broadcast(message, sender_socket):
    """Send message to all clients except sender."""
    for user, client in clients.items():
        if client != sender_socket:
            try:
                client.send(message.encode())
            except:
                del clients[user]


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 5556))
    server.listen(5)
    print("Server started on port 5556...")

    while True:
        client_socket, addr = server.accept()

        # Receive username from the client
        username = client_socket.recv(1024).decode()

        if username in clients:
            client_socket.send("Username already in use!".encode())
            client_socket.close()
            continue

        clients[username] = client_socket
        print(f"{username} connected from {addr}")

        threading.Thread(target=handle_client, args=(
            client_socket, username)).start()


start_server()