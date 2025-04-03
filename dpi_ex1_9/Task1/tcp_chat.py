import argparse
import socket
import threading

clients = {}

def start_server(ip, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_address = (ip, port)
    server_socket.bind(server_address)

    server_socket.listen(1)

    print("Waiting for a connection...")
    connection, client_address = server_socket.accept()
    print("Connection from", client_address)

    receive_thread = threading.Thread(target=receive_messages, args=(connection,))
    receive_thread.start()

    while True:
        message = input()
        if message == "":
            break
        connection.sendall(message.encode("utf-8"))

    connection.close()
    server_socket.close()


def start_client(ip, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Verbinde den Client mit dem Server
    try:
        client_socket.connect((ip, port))
        print(f"Verbunden mit Server {ip}:{port}")
    except ConnectionRefusedError:
        print("Verbindung fehlgeschlagen. Stelle sicher, dass der Server läuft.")
        return
    
    threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()

    # Sende Nachrichten an den Server
    while True:
        message = input()
        if message == "exit":  # Beende den Client, wenn "exit" eingegeben wird
            break
        client_socket.sendall(message.encode('utf-8'))

    client_socket.close()
    print("Verbindung geschlossen.")


def receive_messages(connection):
    # You can reuse this if needed
    while True:
        data = connection.recv(1024)
        if not data:
            break
        print(data.decode("utf-8"))


def main():
    # Sets up the command line interface
    parser = argparse.ArgumentParser()
    parser.add_argument("type", choices={"server", "client"})
    parser.add_argument("--port", default=8989, type=int)
    parser.add_argument("--ip", default="localhost")
    args = parser.parse_args()

    if args.type == "server":
        start_server(args.ip, args.port)
    else:
        start_client(args.ip, args.port)


if __name__ == "__main__":
    main()
