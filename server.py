import socket
import threading
from encryption import encrypt_message, decrypt_message

clients = []


def handle_client(client_socket):
    while True:
        try:
            encrypted_message = client_socket.recv(1024)
            if not encrypted_message:
                break

            message = decrypt_message(encrypted_message)
            print(f"Received: {message}")

            broadcast(message, client_socket)
        except:
            break

    clients.remove(client_socket)
    client_socket.close()


def broadcast(message, sender_socket):
    """Send encrypted messages to all clients except the sender."""
    encrypted_message = encrypt_message(message)
    for client in clients:
        if client != sender_socket:
            try:
                client.send(encrypted_message)
            except:
                clients.remove(client)


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 5556))
    server.listen(5)
    print("Server started on port 5556...")

    while True:
        client_socket, addr = server.accept()
        clients.append(client_socket)
        print(f"New connection: {addr}")

        threading.Thread(target=handle_client, args=(client_socket,)).start()


start_server()