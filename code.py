import socket
import rsa
import threading

class SecureChatClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.public_key, self.private_key = self.check_or_generate_keys()
        self.server_public_key = None

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
                    print("\nReceived:", decrypted_message)
            except:
                break

    def start(self):
        self.sock.connect((self.host, self.port))
        print("Connection on {}".format(self.port))

        # Send our public key to the server
        self.sock.send(self.public_key.save_pkcs1())

        # Receive the server's public key
        self.server_public_key = rsa.PublicKey.load_pkcs1(self.sock.recv(1024))

        # Start a thread to receive messages
        threading.Thread(target=self.receive_messages, daemon=True).start()

        while True:
            message = input("-> ")
            encrypted_message = self.encrypt(message, self.server_public_key)
            self.sock.send(encrypted_message)

        print("Close")
        self.sock.close()


# Usage example
if __name__ == "__main__":
    client = SecureChatClient("192.167.9.185", 15555)
    client.start()
