import socket
import threading

# Server configuration
HOST = '127.0.0.1'
PORT = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = {}


def broadcast(message, sender_socket=None):
    """Send a message to all connected clients except the sender."""
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message)
            except:
                client.close()
                del clients[client]


def handle_client(client_socket):
    """Handle client communication."""
    try:
        # First message from the client should be their username
        username = client_socket.recv(1024).decode('utf-8')
        clients[client_socket] = username
        print(f"{username} has joined the chat.")
        broadcast(f"{username} has joined the chat.".encode(
            'utf-8'), client_socket)

        while True:
            message = client_socket.recv(1024)
            if not message:
                break
            formatted_message = f"{username}: {message.decode('utf-8')}"
            print(formatted_message)
            broadcast(formatted_message.encode('utf-8'), client_socket)

    except:
        pass

    # Remove client on disconnect
    print(f"{clients[client_socket]} has left the chat.")
    broadcast(f"{clients[client_socket]} has left the chat.".encode('utf-8'))
    del clients[client_socket]
    client_socket.close()


def start_server():
    print(f"Server is listening on {HOST}:{PORT}...")
    while True:
        client_socket, _ = server.accept()
        threading.Thread(target=handle_client, args=(client_socket,)).start()


start_server()