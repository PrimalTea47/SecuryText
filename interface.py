import socket
import rsa
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox

class SecureChatClient:
    def __init__(self, host, port, message_display):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.public_key, self.private_key = self.check_or_generate_keys()
        self.server_public_key = None
        self.message_display = message_display

    def check_or_generate_keys(self):
        try:
            with open('pub_key.key', 'rb') as f:
                public_key = rsa.PublicKey.load_pkcs1(f.read())

            with open('private_key.key', 'rb') as f:
                private_key = rsa.PrivateKey.load_pkcs1(f.read())
            return public_key, private_key
        except FileNotFoundError:
            return self.make_keys()

    def make_keys(self):
        publicKey, privateKey = rsa.newkeys(2048)
        with open('pub_key.key', 'wb') as f:
            f.write(publicKey.save_pkcs1())

        with open('private_key.key', 'wb') as f:
            f.write(privateKey.save_pkcs1())
        return publicKey, privateKey

    def encrypt(self, message, public_key):
        encrypted_message = rsa.encrypt(message.encode(), public_key)
        return encrypted_message

    def decrypt(self, encrypted_message):
        decrypted_message = rsa.decrypt(encrypted_message, self.private_key).decode()
        return decrypted_message

    def receive_messages(self):
        while True:
            try:
                encrypted_message = self.sock.recv(1024)
                if encrypted_message:
                    decrypted_message = self.decrypt(encrypted_message)
                    if decrypted_message == "\x00":
                        root.destroy()
                    elif decrypted_message == "":
                        pass
                    else:
                        self.display_message(f"Reçu: {decrypted_message}")
            except Exception as e:
                self.display_message(f"Erreur : {str(e)}")
                break

    def start(self):
        try:
            self.sock.connect((self.host, self.port))
            self.display_message(f"Connecté à {self.host}")

            # Send our public key to the server
            self.sock.send(self.public_key.save_pkcs1())

            # Receive the server's public key
            self.server_public_key = rsa.PublicKey.load_pkcs1(self.sock.recv(1024))

            # Start a thread to receive messages
            threading.Thread(target=self.receive_messages, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Erreur de connection", str(e))

    def send_message(self, message):
        if self.server_public_key and message:
            encrypted_message = self.encrypt(message, self.server_public_key)
            self.sock.send(encrypted_message)
            self.display_message(f"Envoyé: {message}")

    def display_message(self, message):
        self.message_display.config(state=tk.NORMAL)
        self.message_display.insert(tk.END, message + '\n')
        self.message_display.config(state=tk.DISABLED)


class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SecuryText")

        self.ip_label = tk.Label(root, text="IP du serveur:")
        self.ip_label.pack(padx=5, pady=5)

        self.ip_entry = tk.Entry(root)
        self.ip_entry.pack(padx=5, pady=5)

        self.connect_button = tk.Button(root, text="Connecter", command=self.connect_to_server)
        self.connect_button.pack(padx=5, pady=5)

        self.message_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled')
        self.message_display.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        self.message_entry = tk.Entry(root)
        self.message_entry.pack(padx=5, pady=5, fill=tk.X, expand=True)

        self.send_button = tk.Button(root, text="Envoyer (Entrée)", command=self.send_message)
        self.send_button.pack(padx=5, pady=5)

        self.quit_button = tk.Button(root, text="Quitter (Échap)", command=self.quit_server)
        self.quit_button.pack()

        root.bind("<Return>",self.send_message_return)
        root.bind("<Escape>", self.quit_server_return)

        self.client = None

    def connect_to_server(self):
        host = self.ip_entry.get()
        if host:
            self.client = SecureChatClient(host, 15555, self.message_display)
            self.client.start()
            self.ip_entry.config(state='disabled')
            self.connect_button.config(state='disabled')

    def send_message(self):
        message = self.message_entry.get()
        if self.client and message:
            self.client.send_message(message)
            self.message_entry.delete(0, tk.END)

    def send_message_return(self, event):
        message = self.message_entry.get()
        if self.client and message:
            self.client.send_message(message)
            self.message_entry.delete(0, tk.END)

    def quit_server(self):
        self.client.send_message("\x00")
        root.destroy()

    def quit_server_return(self, event):
        self.client.send_message("\x00")
        root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()
