import socket
import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext, filedialog, messagebox
from database import register_user, verify_user
import os
import platform
from pygame import mixer
from plyer import notification

# Initialize pygame mixer
mixer.init()

# Path to the notification sound file
NOTIFICATION_SOUND = "notification.mp3"


class ChatClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure Chat Client")
        self.is_muted = False

        self.username = self.authenticate_user()
        if not self.username:
            return

        self.text_area = scrolledtext.ScrolledText(
            root, wrap=tk.WORD, state='disabled', height=20, width=50)
        self.text_area.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

        self.entry = tk.Entry(root, width=40)
        self.entry.grid(row=1, column=0, padx=10, pady=10)

        self.send_button = tk.Button(
            root, text="Send", command=self.send_message)
        self.send_button.grid(row=1, column=1, padx=10, pady=10)

        self.file_button = tk.Button(
            root, text="Send File", command=self.send_file)
        self.file_button.grid(row=1, column=2, padx=10, pady=10)

        self.mute_button = tk.Button(
            root, text="🔊 Mute", command=self.toggle_mute)
        self.mute_button.grid(row=2, column=0, padx=10, pady=10)   # mute option

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(("127.0.0.1", 5556))

        self.client.send(f"{self.username}:{self.password}".encode())

        response = self.client.recv(1024).decode()
        if response == "LOGIN_FAILED":
            messagebox.showerror("Error", "Invalid credentials!")
            self.root.quit()
            return

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
                    self.password = password
                    return username
                else:
                    messagebox.showerror(
                        "Error", "Invalid username or password!")

    def send_message(self):
        """Sends a message to the server."""
        message = self.entry.get()
        if message:
            self.client.send(message.encode())
            self.entry.delete(0, tk.END)

    def send_file(self):
        """Handles file selection and sending to the server."""
        file_path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("PDF files", "*.pdf"),
                       ("PNG images", "*.png"), ("JPG images", "*.jpg")])
        if not file_path:
            return

        filename = os.path.basename(file_path)
        filesize = os.path.getsize(file_path)

        # Notify server about file transfer
        self.client.send(f"FILE_TRANSFER:{filename}:{filesize}".encode())

        with open(file_path, "rb") as file:
            while chunk := file.read(4096):
                self.client.send(chunk)

        messagebox.showinfo("Success", f"File {filename} sent successfully!")

    def receive_messages(self):
        """Receives messages from the server and updates the UI."""
        while True:
            try:
                message = self.client.recv(1024).decode()
                if not message:
                    break

                if message.startswith("FILE_RECEIVED:"):
                    filename = message.split(":")[1]
                    self.show_notification(
                        "File Received", f"New file received: {filename}")
                else:
                    self.show_notification("New Message", message)

                self.text_area.config(state=tk.NORMAL)
                self.text_area.insert(tk.END, message + "\n")
                self.text_area.config(state=tk.DISABLED)
                self.text_area.yview(tk.END)
            except:
                break

    def show_notification(self, title, message):
        """Displays a system notification and plays a sound."""
        self.play_sound()
        try:
            notification.notify(
                title=title,
                message=message,
                timeout=3  # Notification disappears after 3 seconds
            )
        except Exception as e:
            print("Notification Error:", e)
    
    # option to toggle notification sound
    def toggle_mute(self):
        """Toggles notification sound on/off."""
        self.is_muted = not self.is_muted
        if self.is_muted:
            self.mute_button.config(text="🔇 Unmute")
        else:
            self.mute_button.config(text="🔊 Mute")


    def play_sound(self):
        """Plays a sound alert when a new message arrives."""
        if not self.is_muted:  # Only play if not muted
            try:
                if os.path.exists(NOTIFICATION_SOUND):
                    mixer.music.load(NOTIFICATION_SOUND)
                    mixer.music.play()
                else:
                    print("Notification sound file not found!")
            except Exception as e:
                print("Sound Error:", e)


root = tk.Tk()
app = ChatClient(root)
root.mainloop()