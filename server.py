import socket
import threading

clients = {}  # Speichert {nickname: (IP, port)}
connections = {}  # Speichert aktive Verbindungen {nickname1: nickname2}

def handle_client(server_socket):
    while True:
        data, addr = server_socket.recvfrom(1024)
        message = data.decode('utf-8').split()

        if message[0] == "LOGIN":
            nickname = message[1]
            clients[nickname] = addr
            print(f"{nickname} angemeldet von {addr}")

        elif message[0] == "LOOKUP":
            sender = message[1]
            target = message[2]

            if target in connections or sender in connections:
                server_socket.sendto("BUSY".encode('utf-8'), addr)
            elif target in clients:
                server_socket.sendto(f"{clients[target][0]} {clients[target][1]}".encode('utf-8'), addr)
            else:
                server_socket.sendto("NOT_FOUND".encode('utf-8'), addr)
        
        elif message[0] == "LIST":
            server_socket.sendto(str(clients).encode('utf-8'), addr)

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(("0.0.0.0", 9999))
    print("Server läuft auf Port 5000...")

    thread = threading.Thread(target=handle_client, args=(server_socket,))
    thread.start()

if __name__ == "__main__":
    start_server()
