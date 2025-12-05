import socket
import threading
import json
import time
import tkinter as tk
from tkinter import simpledialog, messagebox
from tkinter import ttk
from ttkthemes import ThemedTk
import emoji

SERVER_IP = "10.0.108.84"
SERVER_PORT = 9999
TIMEOUT = 2
BUFFER_SIZE = 4096

class ChatClient:
    def __init__(self, root):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(TIMEOUT)
        self.username = ""
        self.sent_seq = 0
        self.acks = set()
        self.received_seqs = set()

        self.root = root
        self.root.title("RapideMSN")
        self.root.geometry("500x650")
        self.root.resizable(False, False)

        # Tema claro
        self.root.set_theme("arc")  # Você pode trocar por "plastik" ou "radiance"

        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Área de chat com fundo branco e texto preto
        self.chat_area = tk.Text(
            self.main_frame, wrap=tk.WORD, state=tk.DISABLED,
            width=60, height=20, bg="#000", fg="#000000",
            insertbackground="#000000", font=("Segoe UI", 11), bd=0, relief=tk.FLAT
        )
        self.chat_area.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky="nsew")

        # Campo de entrada de mensagem
        self.msg_entry = ttk.Entry(self.main_frame, width=60, font=("Segoe UI", 11))
        self.msg_entry.grid(row=1, column=0, padx=(0, 10), pady=10, sticky="ew")
        self.msg_entry.bind("<Return>", self.send_message)
        self.msg_entry.bind("<Control-Return>", self.send_message)

        # Botão de enviar
        self.send_btn = ttk.Button(self.main_frame, text="Enviar", command=self.send_message)
        self.send_btn.grid(row=1, column=1, pady=10, padx=(10, 0), sticky="ew")

        # Ajustes de layout
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)

        self.register_username()

        self.recv_thread = threading.Thread(target=self.receive_loop, daemon=True)
        self.recv_thread.start()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        exit_msg = {
            "action": "exit",
            "username": self.username
        }
        try:
            self.sock.sendto(json.dumps(exit_msg).encode(), (SERVER_IP, SERVER_PORT))
        except:
            pass
        self.root.destroy()

    def register_username(self):
        while True:
            self.username = simpledialog.askstring("Nome de usuário", "Digite seu nome:")
            if not self.username:
                self.root.destroy()
                return
            register_msg = json.dumps({"action": "register", "username": self.username})
            self.sock.sendto(register_msg.encode(), (SERVER_IP, SERVER_PORT))
            try:
                response, _ = self.sock.recvfrom(BUFFER_SIZE)
                response = json.loads(response.decode())
                if response.get("status") == "ok":
                    break
                else:
                    messagebox.showerror("Erro", response.get("message"))
            except socket.timeout:
                messagebox.showerror("Timeout", "Servidor não respondeu.")

    def display_message(self, sender, content, align="left"):
        self.chat_area.config(state=tk.NORMAL)
        tag = "right" if align == "right" else "left"
        name = "Você" if sender == self.username else f"{sender}"

        content = emoji.emojize(content, language='alias')
        formatted = f"{name}: {content}\n"
        self.chat_area.insert(tk.END, formatted, tag)

        self.chat_area.tag_config("right", justify=tk.RIGHT, foreground="#1565C0", font=("Segoe UI", 10, "bold"))
        self.chat_area.tag_config("left", justify=tk.LEFT, foreground="#39ff14", font=("Segoe UI", 10))
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.see(tk.END)

    def display_notification(self, message):
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, f"\n{'-'*5} {message} {'-'*5}\n", "center")
        self.chat_area.tag_config("center", justify=tk.CENTER, foreground="#FB8C00", font=("Segoe UI", 10, "italic"))
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.see(tk.END)

    def receive_loop(self):
        while True:
            try:
                data, _ = self.sock.recvfrom(BUFFER_SIZE)
                msg = json.loads(data.decode())
                if msg["action"] == "message":
                    seq = msg["seq"]
                    key = (msg["username"], seq)
                    if key in self.received_seqs:
                        continue
                    self.received_seqs.add(key)
                    self.display_message(msg["username"], msg["content"], align="right")
                elif msg["action"] == "ack":
                    self.acks.add(msg["seq"])
                elif msg["action"] == "notify":
                    self.display_notification(msg["message"])
            except:
                continue

    def send_message(self, event=None):
        content = self.msg_entry.get().strip()
        if not content:
            return
        msg = {
            "action": "message",
            "username": self.username,
            "content": content,
            "seq": self.sent_seq
        }
        msg_data = json.dumps(msg).encode()
        retries = 3
        while retries > 0:
            self.sock.sendto(msg_data, (SERVER_IP, SERVER_PORT))
            time.sleep(TIMEOUT)
            if self.sent_seq in self.acks:
                self.display_message(self.username, content, align="left")
                self.sent_seq += 1
                self.msg_entry.delete(0, tk.END)
                return
            retries -= 1
        messagebox.showerror("Sentimos muito", "Servidor está offline.")

if __name__ == "__main__":
    root = ThemedTk(theme="arc")
    app = ChatClient(root)
    root.mainloop()
