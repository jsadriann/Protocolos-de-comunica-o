# 💬 RapideMSN - Chat em Rede Local via UDP

Um chat simples em Python usando **UDP sockets**, interface gráfica com **Tkinter** e suporte a **emojis**, com tema escuro e confiável em redes locais (LAN).

---

## 🖥️ Requisitos

- Python 3.8+
- Pacotes Python:
  - `ttkthemes`
  - `emoji`

Você pode instalar os pacotes necessários com:

```bash
pip install ttkthemes emoji
```

---

## 🚀 Como Rodar

### 🟢 1. Iniciar o Servidor

No terminal:

```bash
python server.py
```

- O servidor será iniciado automaticamente usando o **IP local da máquina** (ex: `192.168.0.101`).
- Ele escutará na porta `9999` e aceitará conexões de qualquer cliente na mesma rede local (roteador).

---

### 💻 2. Rodar o Cliente

Em outra máquina (ou na mesma), execute:

```bash
python client.py
```

- Será solicitado um **nome de usuário**.
- O cliente tentará se registrar no servidor via IP padrão `127.0.0.1`.
- Se o servidor estiver em outra máquina, **altere a constante `SERVER_IP` no `client.py`** para o IP local do servidor:

```python
SERVER_IP = "192.168.0.101"  # Altere para o IP do servidor
```

---

## 🎨 Recursos da Interface

- Tema escuro (equilux)
- Suporte a **emojis** usando `:nome:`, ex: `:smile:`
- Envio com Enter ou Ctrl+Enter
- Mensagens exibidas com alinhamento por autor
- Notificações de entrada de usuários

---

## 🛠️ Estrutura dos Arquivos

```
📁 seu_projeto/
├── client.py      # Interface gráfica + envio/recebimento de mensagens
├── server.py      # Lida com clientes e transmissão de mensagens
└── README.md      # Este arquivo
```

---

## ❓ Dúvidas Comuns

**O chat funciona em diferentes PCs conectados no mesmo roteador?**  
✅ Sim, desde que o `SERVER_IP` no cliente aponte para o IP correto do servidor.

**Preciso abrir portas no roteador?**  
🚫 Não, se todos os dispositivos estiverem na mesma rede local (LAN).

**Funciona pela internet?**  
🔒 Não diretamente. Para uso externo, seria necessário NAT, redirecionamento de portas ou um servidor em nuvem.

---

## 🧑‍💻 Autor

Desenvolvido por [Seu Nome]. Projeto educativo para comunicação em redes locais usando Python.
