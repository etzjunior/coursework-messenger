import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, simpledialog

# Server connection details
HOST = '127.0.0.1'
PORT = 5555


class ChatClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Messenger")

        # Message display area
        self.text_area = scrolledtext.ScrolledText(
            root, wrap=tk.WORD, state='disabled', height=20, width=50)
        self.text_area.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        # Input field for messages
        self.msg_entry = tk.Entry(root, width=40)
        self.msg_entry.grid(row=1, column=0, padx=10, pady=10)
        # Send message on Enter key
        self.msg_entry.bind("<Return>", self.send_message)

        # Send button
        self.send_button = tk.Button(
            root, text="Send", command=self.send_message)
        self.send_button.grid(row=1, column=1, padx=10, pady=10)

        # Connect to the server
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((HOST, PORT))

        # Get username and send it to server
        self.username = self.get_username()
        self.client.send(self.username.encode('utf-8'))

        # Start receiving messages
        threading.Thread(target=self.receive_messages, daemon=True).start()

    def get_username(self):
        """Ask for username in a simple input dialog."""
        return tk.simpledialog.askstring("Username", "Enter your username:")

    def receive_messages(self):
        while True:
            try:
                message = self.client.recv(1024).decode('utf-8')
                if not message:
                    break
                self.text_area.config(state=tk.NORMAL)
                self.text_area.insert(tk.END, message + "\n")
                self.text_area.config(state=tk.DISABLED)
                self.text_area.yview(tk.END)  # Auto-scroll
            except ConnectionResetError:
                break

    def send_message(self, event=None):
        """Send message to the server."""
        message = self.msg_entry.get()
        if message:
            self.client.send(message.encode('utf-8'))
            self.msg_entry.delete(0, tk.END)

    def display_message(self, message):
        """Display received messages in the text area."""
        self.text_area.config(state='normal')
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.config(state='disabled')
        self.text_area.yview(tk.END)


# Run the chat client GUI
root = tk.Tk()
app = ChatClient(root)
root.mainloop()