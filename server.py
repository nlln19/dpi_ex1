import socket
import threading

clients = {}  # Speichert {nickname: (IP, port)}
connections = {}  # Speichert aktive Verbindungen {nickname1: nickname2}

def handle_client(server):
    while True:
        data, addr = server.recvfrom(1024)
        message = data.decode('utf-8').split()

        if message[0] == "LOGIN":
            nickname = message[1]
            clients[nickname] = addr
            print(f"{nickname} angemeldet von {addr}")

        elif message[0] == "LIST":
            server.sendto(str(clients).encode('utf-8'), addr)

        elif message[0] == "CHECK":
            targetName = message[1]
            if targetName in clients:
                client_info = clients[targetName]
                server.sendto(f"Nickname: {targetName}, IP: {client_info[0]}, Port: {client_info[1]}".encode('utf-8'), addr)
            else:
                server.sendto(f"Nickname {targetName} wurde nicht gefunden...".encode('utf-8'), addr)

        elif message[0] == "CONNECT":
            if message[1] in clients:
                clientIp, clientPort = clients.get(message[1])
                server.sendto(f"{clientIp} {clientPort})".encode('utf-8'), addr)
            else:
                server.sendto("Client doesn't exist".encode('utf-8'), addr)
        

        elif message[0] == "EXIT":
            nickname = message[1]
            print(f"{nickname} abgemeldet")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(("0.0.0.0", 9999))
    print("Server läuft auf Port 9999...")

    thread = threading.Thread(target=handle_client, args=(server,))
    thread.start()

if __name__ == "__main__":
    start_server()

#Momentan funktioniert die connection zwischen zwei Clients nicht...