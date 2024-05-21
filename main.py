import tkinter as tk
import socket
import rsa
import threading
from client import connection_finale

def get_server_ip():
	return ip_serveur.get()



fenetre = tk.Tk()
fenetre.title("SecuryText")
fenetre.geometry("500x500")

frame_haut = tk.Frame(fenetre)
frame_gauche = tk.Frame(frame_haut)
frame_droite = tk.Frame(frame_haut)
frame_bas = tk.Frame(fenetre)

ip_connect = tk.Label(frame_gauche, text="Adresse IP du serveur")
ip_serveur = tk.StringVar()
ip_connect_entry = tk.Entry(frame_gauche, textvariable=ip_serveur)
ip_connect_button = tk.Button(frame_gauche, text="Connecter", command=lambda:connection_finale(get_server_ip()))

message_label = tk.Label(frame_droite, text="Message :")
message = tk.StringVar()
message_entry = tk.Entry(frame_droite, textvariable=message)
message_button = tk.Button(frame_droite, text="Envoyer")

receive_box = tk.Text(frame_bas, width=100, height=40)

##PACK
ip_connect.pack()
ip_connect_entry.pack()
ip_connect_button.pack()
frame_gauche.pack(side='left')

message_label.pack()
message_entry.pack()
message_button.pack()
frame_droite.pack(side='right')

frame_haut.pack()

receive_box.pack()
frame_bas.pack(side='bottom')

fenetre.mainloop()