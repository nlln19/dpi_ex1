import socket
import threading
import argparse
import re
import queue
import sys

class ChatClient:
    def __init__(self, client_ip, server_ip, server_port):
        self.client_ip = client_ip
        self.server_ip = server_ip
        self.server_port = server_port
        self.partner_ip = None
        self.partner_port = None
        self.partner_name = None
        self.in_chat = False
        self.name = ""
        self.input_queue = queue.Queue()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((client_ip, 0))
        self.running = True

    def get_username(self):
        while True:
            self.name = input("Enter your nickname: ").strip()
            self.name = re.sub("\\s+", "", self.name)
            if self.name:
                self.socket.sendto(self.name.encode('utf-8'), (self.server_ip, self.server_port))
                response, _ = self.socket.recvfrom(1024)
                if response.decode('utf-8') != "invalidUsername":
                    print(f"Nickname set: {self.name}")
                    print("Available commands: \n /start <username> --> request a Peer-To-Peer Chat, "
                    "                           \n /list --> lists all online users, "
                    "                           \n /check <username> --> checks the IP and Port of a user, "
                    "                           \n /end --> ends the Chat with the Peer, "
                    "                           \n /exit --> disconnects you from the server.")
                    break
                print("Username taken. Try another.")

    def handle_input(self):
        while self.running:
            try:
                cmd = input()
                self.input_queue.put(cmd)
                parts = cmd.split()

                if parts[0] == "/exit" and len(parts) == 1:
                    self.running = False
                    self.socket.sendto(f"exit {self.name}".encode('utf-8'), (self.server_ip, self.server_port))
                    break

                elif not self.in_chat:
                    if parts[0] == "/start" and len(parts) == 2 and parts[1] != self.name:
                        self.socket.sendto(f"start {parts[1]} {self.name}".encode('utf-8'), (self.server_ip, self.server_port))
                        print("Waiting for response...")
                    elif parts[0] == "/end" and len(parts) == 1:
                        print("Not in a chat.")
                    elif parts[0] == "/list" and len(parts) == 1:
                        self.socket.sendto("list".encode('utf-8'), (self.server_ip, self.server_port))
                    elif parts[0] == "/check" and len(parts) == 2:
                        self.socket.sendto(f"check {parts[1]}".encode('utf-8'), (self.server_ip, self.server_port))

                else:
                    if parts[0] == "/end" and len(parts) == 1:
                        self.in_chat = False
                        self.socket.sendto("chat_end".encode('utf-8'), (self.partner_ip, self.partner_port))
                        self.socket.sendto(f"free {self.name} {self.partner_name}".encode('utf-8'), (self.server_ip, self.server_port))
                        print("Chat ended.")
                    elif parts[0] == "/start" and len(parts) == 2:
                        print("End current chat first.")
                    else:
                        self.socket.sendto(f"{self.name}: {cmd}".encode('utf-8'), (self.partner_ip, self.partner_port))
            except (KeyboardInterrupt, EOFError):
                self.running = False
                break

        if self.in_chat:
            self.socket.sendto(f"free {self.name} {self.partner_name}".encode('utf-8'), (self.server_ip, self.server_port))
            self.socket.sendto("chat_end".encode('utf-8'), (self.partner_ip, self.partner_port))
        self.socket.sendto(f"bye {self.name}".encode('utf-8'), (self.server_ip, self.server_port))
        self.socket.close()

    def handle_messages(self):
        while self.running:
            try:
                msg, addr = self.socket.recvfrom(1024)
                msg = msg.decode('utf-8').split()

                if msg[0] == "accept_chat" and len(msg) == 4:
                    self.in_chat = True
                    self.partner_ip = msg[1]
                    self.partner_port = int(msg[2])
                    self.partner_name = msg[3]
                    print(f"Chatting with: {self.partner_name}")
                
                elif msg[0] == "list":
                    print(msg)

                elif msg[0] == "request_chat" and len(msg) == 2:
                    if self.in_chat:
                        self.socket.sendto(f"busy {msg[1]}".encode('utf-8'), (self.server_ip, self.server_port))
                    else:
                        while not self.input_queue.empty():
                            self.input_queue.get()
                        choice = input(f"Accept chat with {msg[1]}? (y/n): ").strip().lower()
                        while choice not in ["y", "n"]:
                            choice = input("Invalid input. Accept? (y/n): ").strip().lower()
                        if choice == "y":
                            self.socket.sendto(f"ok {msg[1]} {self.name}".encode('utf-8'), (self.server_ip, self.server_port))
                        else:
                            self.socket.sendto(f"no {msg[1]}".encode('utf-8'), (self.server_ip, self.server_port))

                elif msg[0] == "chat_end" and len(msg) == 1:
                    self.in_chat = False
                    print(f"{self.partner_name} left the chat.")

                else:
                    print(" ".join(msg))
            except OSError:
                if self.running:
                    raise
                break

    def run(self):
        self.get_username()
        receive_thread = threading.Thread(target=self.handle_messages)
        receive_thread.start()
        self.handle_input()
        receive_thread.join()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="0.0.0.0")
    parser.add_argument("--serverPort", type=int, default=8989)
    parser.add_argument("--serverIp", default="localhost")
    args = parser.parse_args()
    client = ChatClient(args.ip, args.serverIp, args.serverPort)
    client.run()

if __name__ == "__main__":
    main()