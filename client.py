import socket
import threading
import tkinter as tk
from tkinter import scrolledtext
from encryption import encrypt_message, decrypt_message


class ChatClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure Chat Client")

        self.text_area = scrolledtext.ScrolledText(
            root, wrap=tk.WORD, state='disabled', height=20, width=50)
        self.text_area.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        self.entry = tk.Entry(root, width=40)
        self.entry.grid(row=1, column=0, padx=10, pady=10)

        self.send_button = tk.Button(
            root, text="Send", command=self.send_message)
        self.send_button.grid(row=1, column=1, padx=10, pady=10)

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(("127.0.0.1", 5556))

        threading.Thread(target=self.receive_messages, daemon=True).start()

    def send_message(self):
        message = self.entry.get()
        if message:
            encrypted_message = encrypt_message(message)
            self.client.send(encrypted_message)
            self.entry.delete(0, tk.END)

    def receive_messages(self):
        while True:
            try:
                encrypted_message = self.client.recv(1024)
                if not encrypted_message:
                    break

                message = decrypt_message(encrypted_message)
                self.text_area.config(state=tk.NORMAL)
                self.text_area.insert(tk.END, message + "\n")
                self.text_area.config(state=tk.DISABLED)
                self.text_area.yview(tk.END)
            except:
                break


root = tk.Tk()
app = ChatClient(root)
root.mainloop()