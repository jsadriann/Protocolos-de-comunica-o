import socket
import threading
import json

##SERVER_IP = "0.0.0.0"
# Obter IP local
hostname = socket.gethostname()
SERVER_IP = socket.gethostbyname(hostname)

# Nome do servidor
SERVER_NAME = "Servidor do RapideMSN"

SERVER_PORT = 9999
clients = {}
received_messages = set()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((SERVER_IP, SERVER_PORT))

def notify_users(message, exclude_user=None):
    for user, user_addr in clients.items():
        if user != exclude_user:
            notification = {
                "action": "notify",
                "message": message
            }
            sock.sendto(json.dumps(notification).encode(), user_addr)

def handle_message(data, addr):
    try:
        msg = json.loads(data.decode())
        action = msg.get("action")

        if action == "register":
            username = msg["username"]
            if username in clients:
                response = {"status": "error", "message": "Username already taken"}
                sock.sendto(json.dumps(response).encode(), addr)
            else:
                clients[username] = addr
                response = {"status": "ok"}
                sock.sendto(json.dumps(response).encode(), addr)
                print(f"[+] {username} connected from {addr}")

                # Notifica todos os clientes sobre a nova conexão, mas não para o usuário atual
                notify_users(f"{username} entrou no grupo.", exclude_user=username)

        elif action == "message":
            username = msg["username"]
            seq = msg["seq"]
            key = (username, seq)

            if key in received_messages:
                return

            received_messages.add(key)
            content = msg["content"]

            ack = {"action": "ack", "seq": seq}
            sock.sendto(json.dumps(ack).encode(), addr)

            print(f"[{username}] {content}")

            for user, user_addr in clients.items():
                if user != username:
                    forward = {
                        "action": "message",
                        "username": username,
                        "content": content,
                        "seq": seq
                    }
                    sock.sendto(json.dumps(forward).encode(), user_addr)

    except Exception as e:
        print(f"[ERROR] {e}")

def listen():
    print(f"[{SERVER_NAME}] Online em {SERVER_IP}:{SERVER_PORT}")
    while True:
        try:
            data, addr = sock.recvfrom(4096)
            threading.Thread(target=handle_message, args=(data, addr), daemon=True).start()
        except KeyboardInterrupt:
            print(f"\n[{SERVER_NAME}] Encerrando servidor.")
            break


if __name__ == "__main__":
    listen()
