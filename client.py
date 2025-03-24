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

    print("Befehle: (exit / list / check / connect <nickname>)")

    while True:
        message = input()
        
        if message.startswith("list"):
            client.sendto(f"LIST".encode('utf-8'), server_address)
            data, _ = client.recvfrom(1024)
            response = data.decode('utf-8')
            print(response)
        
        elif message.startswith("check"):
             nickname_to_check = message.split()[1]  
             client.sendto(f"CHECK {nickname_to_check}".encode('utf-8'), server_address)
             data, _ = client.recvfrom(1024)  
             response = data.decode('utf-8')  
             print(response)

        
        elif message.startswith("connect"):
            print("1")
            client.sendto(f"CONNECT {message.split()[1]} {nickname}".encode('utf-8'), server_address)
            print("2")
            p2pIp, p2pPort = client.recvfrom(1024)
            p2p_adress = (p2pIp, p2pPort)
            print("3")
            p2p_Chat(client, p2p_adress)

        elif message == "exit":
            client.sendto(f"EXIT {nickname}".encode('utf-8'), server_address)
            break


    client.close()

def p2p_Chat(client, p2p_adress):
    print("4")
    print(f"Verbinde mit {p2p_adress}")
    while True:
        message = input()
        client.sendto(message.encode('utf-8'), (p2p_adress))

        if message == "exit":
            break

        thread = threading.Thread(target=p2p_Chat, args=(client, p2p_adress))
        thread.start()
    return

if __name__ == "__main__":
    start_client()
