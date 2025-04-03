import socket
import threading
import argparse
import time

class PeerToPeerChat:
    def __init__(self, nickname, local_ip="0.0.0.0", broadcast_ip="255.255.255.255", port=8989):
        self.nickname = nickname
        self.broadcast_ip = broadcast_ip
        self.port = port
        self.peers = {}
        self.current_chat = None
        self.running = True
        
        self.broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        
        self.direct_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.direct_socket.bind((local_ip, 0))	# 0 = random port
        self.direct_port = self.direct_socket.getsockname()[1]
        
        threading.Thread(target=self.listen_for_broadcasts, daemon=True).start()
        threading.Thread(target=self.listen_for_messages, daemon=True).start()
        
        #sendet nachrichten an das gesamte netzwerk 255.255.255.255:8989
    def broadcast(self, message):
        self.broadcast_socket.sendto(message.encode(), (self.broadcast_ip, self.port))
        
        #sendet nachricht an peer
    def send_direct(self, peer_nick, message):
        if peer_nick in self.peers:
            self.direct_socket.sendto(message.encode(), self.peers[peer_nick])
        else:
            print("[Peer not found]")
        
        #listened auf broadcast messages
    def listen_for_broadcasts(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as temp_socket:
            temp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            temp_socket.bind(('0.0.0.0', self.port))
            
            while self.running:
                try:
                    data, addr = temp_socket.recvfrom(1024)
                    msg = data.decode().split()
                    
                    if msg[0] == "HELLO" and msg[1] != self.nickname:
                        self.peers[msg[1]] = (addr[0], int(msg[2]))
                        
                        self.direct_socket.sendto(
                            f"PEER_INFO {self.nickname} {self.direct_port}".encode(),
                            (addr[0], int(msg[2]))
                        )
                        print("[BROADCAST]: " + f"{msg[1]} joined the network")
                        
                    elif msg[0] == "GOODBYE" and msg[1] in self.peers:
                        del self.peers[msg[1]]
                        print("[BROADCAST]: " + f"{msg[1]} left the network")
                        
                except socket.error:
                    if not self.running:
                        break
                    continue
                
    #listened auf direct messages von peers
    def listen_for_messages(self):
        while self.running:
            try:
                data, addr = self.direct_socket.recvfrom(1024)
                msg = data.decode().split(maxsplit=2)
                
                if msg[0] == "PEER_INFO":
                    self.peers[msg[1]] = (addr[0], int(msg[2]))
                    
                elif msg[0] == "CHAT_INVITE":
                    if self.current_chat:
                        self.send_direct(msg[1], "BUSY")
                    else:
                        print(f"[Chat request from {msg[1]}. Accept? (y/n)]: ", end="", flush=True)
                        choice = input().lower()
                        if choice == "y":
                            self.current_chat = msg[1]
                            self.send_direct(msg[1], f"CHAT_ACCEPT {self.nickname}")
                            print(f"[Now chatting with {msg[1]}]")
                        else:
                            self.send_direct(msg[1], f"CHAT_DECLINE {self.nickname}")
                            print(f"[Chat request from {msg[1]} declined]")
                            
                elif msg[0] == "CHAT_ACCEPT":
                    self.current_chat = msg[1]
                    print(f"[{msg[1]} accepted your chat request]")
                    
                elif msg[0] == "CHAT_DECLINE":
                    print(f"[{msg[1]} declined your chat request]")
                    
                elif msg[0] == "BUSY":
                    print(f"[{msg[1]} is already in a chat]")
                    
                elif msg[0] == "MESSAGE":
                    print(f"[{msg[1]}]: {msg[2]}")
                    
                elif msg[0] == "END_CHAT":
                    print(f"[{msg[1]} ended the chat]")
                    self.current_chat = None
                    
            except socket.error:
                if not self.running:
                    break
                continue

    #input vom user handlen
    def start(self):
        self.broadcast(f"HELLO {self.nickname} {self.direct_port}")
        
        print("[Commands]: /list --> list online peers, \n"
		" 	    /start <name> --> start chat with peer, \n"
		" 	    /msg <text> --> send message to current chat with peer, \n"
		" 	    /end --> end current chat, \n"
		" 	    /exit --> exit chat")
        while self.running:
            try:
                cmd = input().strip()
                
                if cmd == "/exit":
                    self.broadcast(f"GOODBYE {self.nickname}")
                    self.running = False
                    
                elif cmd == "/list":
                    print("[Online peers]:", ", ".join(self.peers.keys()) if self.peers else "None")
                    
                elif cmd.startswith("/start "):
                    peer = cmd[7:]
                    if peer in self.peers:
                        self.send_direct(peer, f"CHAT_INVITE {self.nickname}")
                        print("[Waiting for response...]")
                    else:
                        print("[Peer not found]")
                        
                elif cmd.startswith("/msg ") and self.current_chat:
                    message = cmd[5:]
                    self.send_direct(self.current_chat, f"MESSAGE {self.nickname} {message}")
                    
                elif cmd == "/end" and self.current_chat:
                    self.send_direct(self.current_chat, f"END_CHAT {self.nickname}")
                    self.current_chat = None
                    print("[Chat ended]")
                    
                else:
                    print("[Invalid command or not in a chat]")
                    
            except KeyboardInterrupt:
                self.broadcast(f"GOODBYE {self.nickname}")
                self.running = False

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("nickname", help="Your chat nickname")
    parser.add_argument("--port", type=int, default=8989, help="Broadcast port")
    parser.add_argument("--ip", default="255.255.255.255", help="Broadcast IP")
    args = parser.parse_args()
    
    chat = PeerToPeerChat(args.nickname, broadcast_ip=args.ip, port=args.port)
    chat.start()