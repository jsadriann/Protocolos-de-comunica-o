import socket
import threading
import json

# Obter IP local da máquina
hostname = socket.gethostname()
SERVER_IP = socket.gethostbyname(hostname)

# Nome do servidor e porta
SERVER_NAME = "Servidor do RapideMSN"
SERVER_PORT = 9999

# Dicionário de clientes e mensagens recebidas
clients = {}
received_messages = {}

# Socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((SERVER_IP, SERVER_PORT))

#metodo para notificação
def notify_users(message, exclude_user=None):
    for user, user_addr in clients.items():
        if user != exclude_user:
            notification = {
                "action": "notify",
                "message": message
            }
            sock.sendto(json.dumps(notification).encode(), user_addr)

#tratamento das mensagens a serem enviadas
def handle_message(data, addr):
    try:
        msg = json.loads(data.decode())
        action = msg.get("action")

        if action == "register":
            username = msg["username"]

            # Atualiza o IP/porta do usuário mesmo se já estiver registrado
            previous_addr = clients.get(username)
            clients[username] = addr  # Adiciona o cliente

            if previous_addr != addr:
                print(f"[+] {username} (re)conectou de {addr}")
                notify_users(f"{username} entrou.", exclude_user=username)

            # Resetar histórico de mensagens recebidas ao registrar
            received_messages[username] = set()  # Limpa histórico

            response = {"status": "ok"}
            sock.sendto(json.dumps(response).encode(), addr)

        elif action == "message":
            username = msg["username"]
            seq = msg["seq"]

            # Garante que o usuário tem um conjunto de mensagens rastreadas
            if username not in received_messages:
                received_messages[username] = set()

            if seq in received_messages[username]:
                return  # Ignora duplicatas

            received_messages[username].add(seq)
            content = msg["content"]

            # Envia ACK
            ack = {"action": "ack", "seq": seq}
            sock.sendto(json.dumps(ack).encode(), addr)

            print(f"[{username}] {content}")

            # Repassa mensagem para os outros clientes
            for user, user_addr in clients.items():
                if user != username:
                    forward = {
                        "action": "message",
                        "username": username,
                        "content": content,
                        "seq": seq
                    }
                    sock.sendto(json.dumps(forward).encode(), user_addr)

        elif action == "exit":
            username = msg["username"]
            if username in clients:
                del clients[username]
            if username in received_messages:
                del received_messages[username]  # remove o historico do usuario que saiu
            print(f"[-] {username} saiu.")
            notify_users(f"{username} saiu.", exclude_user=username)

    except Exception as e:
        print(f"[ERRO] {e}")

#servidor fica disponivel para responder requisições
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
