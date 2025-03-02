import socket
import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox
from database import register_user, verify_user


class ChatClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure Chat Client")

        self.username = self.authenticate_user()  # Ask for login or register
        if not self.username:
            return  # Exit if authentication failed

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

        # Send username to the server for authentication
        self.client.send(self.username.encode())

        threading.Thread(target=self.receive_messages, daemon=True).start()

    def authenticate_user(self):
        """Handles user authentication via login or registration."""
        while True:
            choice = simpledialog.askstring(
                "Authentication", "Login (L) or Register (R)?").strip().lower()
            if choice not in ['l', 'r']:
                messagebox.showerror("Error", "Invalid choice! Enter L or R.")
                continue

            username = simpledialog.askstring(
                "Username", "Enter your username:")
            password = simpledialog.askstring(
                "Password", "Enter your password:", show='*')

            if not username or not password:
                messagebox.showerror(
                    "Error", "Username and password cannot be empty!")
                continue

            if choice == 'r':
                success = register_user(username, password)
                if success:
                    messagebox.showinfo(
                        "Success", "Registration successful! You can now log in.")
                else:
                    messagebox.showerror("Error", "Username already exists!")
            elif choice == 'l':
                if verify_user(username, password):
                    messagebox.showinfo("Success", "Login successful!")
                    return username  # Return username for chat
                else:
                    messagebox.showerror(
                        "Error", "Invalid username or password!")

    def send_message(self):
        message = self.entry.get()
        if message:
            self.client.send(message.encode())
            self.entry.delete(0, tk.END)

    def receive_messages(self):
        while True:
            try:
                message = self.client.recv(1024).decode()
                if not message:
                    break

                self.text_area.config(state=tk.NORMAL)
                self.text_area.insert(tk.END, message + "\n")
                self.text_area.config(state=tk.DISABLED)
                self.text_area.yview(tk.END)
            except:
                break


root = tk.Tk()
app = ChatClient(root)
root.mainloop()