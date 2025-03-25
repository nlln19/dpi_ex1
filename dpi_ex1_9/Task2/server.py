import socket
import argparse

class ChatServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = {}
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((host, port))
        self.running = True

    def run(self):
        print("Server running.")
        while self.running:
            try:
                msg, (ip, port) = self.socket.recvfrom(1024)
                msg = msg.decode('utf-8').split()

                if not msg:
                    continue

                if (ip, port) not in self.clients.values():
                    if msg[0] not in self.clients and msg[0] != "bye":
                        self.clients[msg[0]] = (ip, port)
                        self.socket.sendto("Connected.".encode('utf-8'), (ip, port))
                        print(f"{msg[0]} joined.")
                    else:
                        self.socket.sendto("invalidUsername".encode('utf-8'), (ip, port))

                elif msg[0] == "start" and len(msg) == 3:
                    if msg[1] in self.clients:
                        target_ip, target_port = self.clients[msg[1]]
                        self.socket.sendto(f"request_chat {msg[2]}".encode('utf-8'), (target_ip, target_port))
                    else:
                        self.socket.sendto("User not found.".encode('utf-8'), (ip, port))

                elif msg[0] == "list":
                    if len(self.clients) > 1:
                        online_users = ", ".join(list(self.clients.keys()))
                        self.socket.sendto(f"Online users: {online_users}".encode('utf-8'), (ip, port))
                    else:
                        self.socket.sendto("No other users online".encode('utf-8'), (ip, port))

                elif msg[0] == "check" and len(msg) == 2:
                    if msg[1] in self.clients:
                        target_ip, target_port = self.clients[msg[1]]
                        self.socket.sendto(f"User {msg[1]} - IP: {target_ip}, Port: {target_port}".encode('utf-8'), (ip, port))
                    else:
                        self.socket.sendto("User not found.".encode('utf-8'), (ip, port))

                elif msg[0] == "busy" and len(msg) == 2:
                    if msg[1] in self.clients:
                        target_ip, target_port = self.clients[msg[1]]
                        self.socket.sendto("User busy.".encode('utf-8'), (target_ip, target_port))

                elif msg[0] == "ok" and len(msg) == 3:
                    if msg[1] in self.clients:
                        target_ip, target_port = self.clients[msg[1]]
                        self.socket.sendto(f"accept_chat {target_ip} {target_port} {msg[1]}".encode('utf-8'), (ip, port))
                        self.socket.sendto(f"accept_chat {ip} {port} {msg[2]}".encode('utf-8'), (target_ip, target_port))
                        print(f"{msg[1]} and {msg[2]} are now chatting.")

                elif msg[0] == "no" and len(msg) == 2:
                    if msg[1] in self.clients:
                        target_ip, target_port = self.clients[msg[1]]
                        self.socket.sendto("Request denied.".encode('utf-8'), (target_ip, target_port))

                elif msg[0] == "free" and len(msg) == 3:
                    print(f"{msg[1]} and {msg[2]} are now free.")

                elif msg[0] == "bye" and len(msg) == 2:
                    if msg[1] in self.clients:
                        del self.clients[msg[1]]
                        print(f"{msg[1]} left.")

                
                elif msg[0] == "exit" and len(msg) == 2:
                    try:
                        if msg[1] in self.clients:
                            del self.clients[msg[1]]
                            print(f"{msg[1]} left.")
                    except ConnectionResetError:
                        print(msg[1] + " disconnected.")
                        continue

            # Server Absturz handlen
            except ConnectionResetError:
                print("Client disconnected abruptly.")
                continue
            except OSError as e:
                if not self.running:
                    break
                print(f"Socket error: {e}")
                continue
            except Exception as e:
                print(f"Unexpected error: {e}")
                continue

    def shutdown(self):
        self.running = False
        self.socket.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8989)
    parser.add_argument("--ip", default="localhost")
    args = parser.parse_args()
    server = ChatServer(args.ip, args.port)
    try:
        server.run()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()

if __name__ == "__main__":
    main()