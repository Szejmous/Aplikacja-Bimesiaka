import tkinter as tk
from tkinter import scrolledtext
import threading
import json
from websocket import WebSocketApp
import socket

# Pobierz nazwę komputera jako identyfikator użytkownika
client_name = socket.gethostname()

# Funkcja do odbierania wiadomości z WebSocketu
def on_message(ws, message):
    data = json.loads(message)
    chat_window.config(state=tk.NORMAL)
    chat_window.insert(tk.END, f"{data['user']}: {data['message']}\n")
    chat_window.config(state=tk.DISABLED)
    chat_window.yview(tk.END)

def on_error(ws, error):
    print(f"Błąd: {error}")

def on_close(ws, close_status_code, close_msg):
    print("Połączenie zamknięte")

def on_open(ws):
    chat_window.config(state=tk.NORMAL)
    chat_window.insert(tk.END, f"System: Połączono jako {client_name}\n")
    chat_window.config(state=tk.DISABLED)

# Funkcja do wysyłania wiadomości
def send_message():
    message = entry.get()
    if message:
        ws.send(json.dumps({"message": message}))
        entry.delete(0, tk.END)

# Uruchom WebSocket w osobnym wątku
def start_websocket():
    global ws
    ws = WebSocketApp(
        "ws://localhost:8000/ws",  # Lokalnie, na Render zmienimy na adres serwera
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()

# Główne okno chatu
chat_root = tk.Tk()
chat_root.title(f"Chat - {client_name}")
chat_root.geometry("400x500")

# Pole do wyświetlania wiadomości
chat_window = scrolledtext.ScrolledText(chat_root, wrap=tk.WORD, state=tk.DISABLED, height=20, width=50)
chat_window.pack(padx=10, pady=10)

# Pole do wpisywania wiadomości
entry = tk.Entry(chat_root, width=40)
entry.pack(padx=10, pady=5, side=tk.LEFT)

# Przycisk do wysyłania wiadomości
send_button = tk.Button(chat_root, text="Wyślij", command=send_message)
send_button.pack(padx=10, pady=5, side=tk.RIGHT)

# Uruchom WebSocket w osobnym wątku
threading.Thread(target=start_websocket, daemon=True).start()

chat_root.mainloop()