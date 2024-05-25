import socket
import rsa
import threading
import os


def checkkey():
    try:
        with open('pub_key.key', 'rb') as f:
            public_key = rsa.PublicKey.load_pkcs1(f.read())

        with open('private_key.key', 'rb') as f:
            private_key = rsa.PrivateKey.load_pkcs1(f.read())

        return public_key, private_key
    except FileNotFoundError:
        return False


def make_key():
    publicKey, privateKey = rsa.newkeys(2048)
    with open('pub_key.key', 'wb') as f:
        f.write(publicKey.save_pkcs1())

    with open('private_key.key', 'wb') as f:
        f.write(privateKey.save_pkcs1())


if not checkkey():
    make_key()

public_key, private_key = checkkey()


def encrypt(message, public_key):
    encrypted_message = rsa.encrypt(message.encode(), public_key)
    return encrypted_message


def decrypt(encrypted_message, private_key):
    decrypted_message = rsa.decrypt(encrypted_message, private_key).decode()
    return decrypted_message


def receive_messages(client, private_key):
    while True:
        try:
            encrypted_message = client.recv(1024)
            if encrypted_message:
                decrypted_message = decrypt(encrypted_message, private_key)
                if decrypted_message == "\x00":
                    os._exit(0)
                    break
                print("\nReceived:", decrypted_message)
                
            elif decrypted_message == "":
                pass

        except:
            break

print("The server IP address :",socket.gethostbyname(socket.gethostname()))
print('Send "EXIT" to end the conversation (Do not use Ctrl+C)')
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('', 15555))
sock.listen(5)
client, address = sock.accept()
print("{} connected".format(address))
client_public_key = rsa.PublicKey.load_pkcs1(client.recv(1024))
client.send(public_key.save_pkcs1())
threading.Thread(target=receive_messages, args=(client, private_key), daemon=True).start()
while True:
    message = input()
    if message == "EXIT":
        encrypted_message = encrypt("\x00", client_public_key)
        client.send(encrypted_message)
        sock.close()
        exit()
    
    else:
        encrypted_message = encrypt(message, client_public_key)
        client.send(encrypted_message)
