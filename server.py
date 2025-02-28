import socket
import threading

# server configuration
HOST = "127.0.0.1"
PORT = 5005

# handles new clients
def handle_client(client_socket, address):
    print(f"[NEW CONNECTION] {address} connected.")

# listens for new connections
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(f"[{address}] {message}")
        except ConnectionResetError:
            break

    print(f"[DISCONNECTED] {address} disconnected.")
    client_socket.close()

# Start the server
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"[SERVER STARTED] Listening on {HOST}:{PORT}")

    while True:
        client_socket, address = server.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket, address), daemon=True)
        thread.start()

        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


if __name__ == "__main__":
    start_server()