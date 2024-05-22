import socket
import rsa
import threading





def connection_finale(hote:str, port=15555):

    # petite fonction pour checker si on à déjà les clé. Si oui on utilise  rsa.PublicKey.load_pkcs1 pour que rsa puisse loader correctement les clés
    def checkkey():
        try:
            with open('pub_key.key', 'rb') as f:
                public_key = rsa.PublicKey.load_pkcs1(f.read())

            with open('private_key.key', 'rb') as f:
                private_key = rsa.PrivateKey.load_pkcs1(f.read())

            return public_key, private_key
        except FileNotFoundError:
            return False

    # Génération de clé dans des formats compréhensible de la librairie
    def make_key():
        publicKey, privateKey = rsa.newkeys(2048)
        with open('pub_key.key', 'wb') as f:
            f.write(publicKey.save_pkcs1())

        with open('private_key.key', 'wb') as f:
            f.write(privateKey.save_pkcs1())


    if not checkkey():
        make_key()

    public_key, private_key = checkkey()

    # Voir la doc de rsa si tu comprend pas
    def encrypt(message, public_key):
        encrypted_message = rsa.encrypt(message.encode(), public_key)
        return encrypted_message

    # Voir la doc de rsa si tu comprend pas
    def decrypt(encrypted_message, private_key):
        decrypted_message = rsa.decrypt(encrypted_message, private_key).decode()
        return decrypted_message


    def receive_messages(sock, private_key):
        while True:
            try:
                encrypted_message = sock.recv(1024)
                if encrypted_message:
                    decrypted_message = decrypt(encrypted_message, private_key)
                    print("\nReceived:", decrypted_message)
            except:
                break


    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((hote, port))
    print("Connection on {}".format(port))

    # On envoie la clé publique à l'autre
    sock.send(public_key.save_pkcs1())

    # On recoie la clé publique de l'autre
    server_public_key = rsa.PublicKey.load_pkcs1(sock.recv(1024))

    # Donc ici je démarre un tread pour que chacun puisse à la fois recevoir et envoyer des messages
    threading.Thread(target=receive_messages, args=(sock, private_key), daemon=True).start()

    while True:
        message = input()
        if message == "exit":
            sock.close()
            break

        encrypted_message = encrypt(message, server_public_key)
        sock.send(encrypted_message)


connection_finale("192.167.16.167",15555)