import socket
import threading

HOST = '127.0.0.1'
PORT = 5555

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

# Get the username and send it to the server
username = input("Enter your username: ")
client.send(username.encode('utf-8'))


def receive_messages():
    """Receive messages from the server and display them."""
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if not message:
                break
            print(message)
        except:
            print("Disconnected from the server.")
            break


# Start listening for messages
threading.Thread(target=receive_messages, daemon=True).start()

# Send messages to the server
while True:
    message = input()
    if message.lower() == "exit":
        break
    client.send(message.encode('utf-8'))

client.close()