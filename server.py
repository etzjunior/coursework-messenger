import socket
import threading
import os
from datetime import datetime
from database import verify_user, register_user


clients = {}  # Stores connected clients


def handle_client(client_socket, username):
    """Handles receiving and broadcasting messages for a client."""
    while True:
        try:
            message = client_socket.recv(1024).decode()
            if not message:
                break

            if message.startswith("FILE_TRANSFER:"):
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                filename, filesize = message[len("FILE_TRANSFER:"):].split(":")
                filesize = int(filesize)
                broadcast(f"[{timestamp}] {username} is sending file: {filename}", client_socket)
                handle_file_transfer(client_socket, filename, filesize)
            else:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                broadcast(f"[{timestamp}] {username}: {message}", client_socket)
        except:
            break

    del clients[username]
    client_socket.close()


def handle_file_transfer(client_socket, filename, filesize):
    """Handles receiving a file from a client in chunks and saving it."""
    save_dir = "received_files"
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, filename)

    received_size = 0
    with open(save_path, "wb") as file:
        while received_size < filesize:
            chunk = client_socket.recv(4096)
            if not chunk:
                break
            file.write(chunk)
            received_size += len(chunk)

    print(f"File received: {filename} ({filesize} bytes)")
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    broadcast(f"[{timestamp}] FILE_RECEIVED:{filename}", client_socket)


def broadcast(message, sender_socket):
    """Send message to all clients except sender."""
    for user, client in clients.items():
        if client != sender_socket:
            try:
                client.send(message.encode())
            except:
                del clients[user]


def start_server():
    """Starts the chat server and handles incoming connections."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 5556))
    server.listen(5)
    print("Server started on port 5556...")

    while True:
        client_socket, addr = server.accept()

        # Receive username and password
        credentials = client_socket.recv(1024).decode().split(":")
        if len(credentials) != 2:
            client_socket.close()
            continue

        username, password = credentials

        if username in clients:
            client_socket.send("USERNAME_TAKEN".encode())
            client_socket.close()
            continue

        if verify_user(username, password):
            client_socket.send("LOGIN_SUCCESS".encode())
        else:
            client_socket.send("LOGIN_FAILED".encode())
            client_socket.close()
            continue

        clients[username] = client_socket
        print(f"{username} connected from {addr}")

        threading.Thread(target=handle_client, args=(
            client_socket, username)).start()


start_server()