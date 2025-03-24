import socket
import threading

def listen_for_messages(client):
    while True:
        try:
            data, addr = client.recvfrom(1024)
            print("\nNachricht:", data.decode('utf-8'))
        except:
            break

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ("127.0.0.1", 9999)

    nickname = input("Gib deinen Nickname ein: ")
    client.sendto(f"LOGIN {nickname}".encode('utf-8'), server_address)

    print("Befehle: (lookup <nickname> / message <ip> <port> / exit")

    while True:
        message = input()

        if message.startswith("lookup"):
            _, target = message.split()
            client.sendto(f"LOOKUP {nickname} {target}".encode('utf-8'), server_address)
            data, _ = client.recvfrom(1024)
            response = data.decode('utf-8')

            if response == "BUSY":
                print("Der Nutzer ist bereits in einem Gespräch!")
            elif response == "NOT_FOUND":
                print("Nutzer nicht gefunden!")
            else:
                ip, port = response.split()
                print(f"Verbinde mit {target} unter {ip}:{port}...")
                client.sendto(f"REQUEST {nickname}".encode('utf-8'), (ip, int(port)))

        elif message.startswith("message"):
            _, ip, port = message.split()
            message = input("Nachricht: ")
            client.sendto(message.encode('utf-8'), (ip, int(port)))
        
        elif message.startswith("list"):
            client.sendto(f"LIST".encode('utf-8'), server_address)
            data, _ = client.recvfrom(1024)
            response = data.decode('utf-8')
            print(response)

        elif message == "exit":
            break


    client.close()

if __name__ == "__main__":
    start_client()
