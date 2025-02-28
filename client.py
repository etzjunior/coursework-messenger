import socket

# server configuration
HOST = "127.0.0.1"
PORT = 5005

# Start Client
def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    while True:
        message = input("You: ")
        if message.lower() == "exit":
            break

        client.send(message.encode('utf-8'))
        response = client.recv(1024).decode('utf-8')
        print(f"Server: {response}")

    client.close()
    print("Disconnected from server.")


if __name__ == "__main__":
    start_client()