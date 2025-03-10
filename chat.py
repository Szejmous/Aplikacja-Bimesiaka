import tkinter as tk
from tkinter import scrolledtext
import threading
import json
from websocket import WebSocketApp
import socket
import base64
from io import BytesIO
from PIL import Image, ImageTk
import pyperclip  # Do obsługi schowka

# Pobierz nazwę komputera jako identyfikator użytkownika
computer_name = socket.gethostname()

# Mapa nazw komputerów do imion
user_names = {
    "BIMES_3": "Mateusz",
    "BIMES_11": "Arek",
    "BIMES_2": "Natalia",
    "KNKPK": "Arek Dom"
}

# Przypisz nazwę użytkownika, jeśli jest w mapie, inaczej użyj nazwy komputera
client_name = user_names.get(computer_name, computer_name)

# Funkcja do odbierania wiadomości z WebSocketu
def on_message(ws, message):
    data = json.loads(message)
    chat_window.config(state=tk.NORMAL)
    if "image" in data:  # Jeśli wiadomość zawiera obraz
        img_data = base64.b64decode(data["image"])
        img = Image.open(BytesIO(img_data))
        photo = ImageTk.PhotoImage(img)
        chat_window.image_create(tk.END, image=photo)
        chat_window.insert(tk.END, f"\n{data['user']}: [Obraz]\n")
        chat_window.image_refs.append(photo)  # Zachowaj referencję, aby obraz się nie usunął
    else:  # Zwykła wiadomość tekstowa
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
    ws.send(json.dumps({"user": client_name}))

# Funkcja do wysyłania wiadomości
def send_message(event=None):  # Dodano opcjonalny parametr event dla Enter
    message = entry.get().strip()
    if message:
        ws.send(json.dumps({"user": client_name, "message": message}))
        entry.delete(0, tk.END)
    return "break"  # Zapobiega domyślnemu zachowaniu Enter (np. nowa linia)

# Funkcja do wklejania obrazu ze schowka
def paste_image(event):
    try:
        # Sprawdź, czy w schowku jest obraz
        img = ImageGrab.grabclipboard()
        if img:
            # Konwertuj obraz na base64
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
            ws.send(json.dumps({"user": client_name, "image": img_base64}))
            entry.delete(0, tk.END)  # Wyczyść pole tekstowe po wklejeniu
        else:
            print("Brak obrazu w schowku")
    except Exception as e:
        print(f"Błąd wklejania obrazu: {e}")
    return "break"

# Uruchom WebSocket w osobnym wątku
def start_websocket():
    global ws
    ws = WebSocketApp(
        "wss://serwer-chatu.onrender.com/ws",
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
chat_window.image_refs = []  # Lista do przechowywania referencji obrazów

# Pole do wpisywania wiadomości
entry = tk.Entry(chat_root, width=40)
entry.pack(padx=10, pady=5, side=tk.LEFT)
entry.bind("<Return>", send_message)  # Wiązanie Enter z wysyłaniem wiadomości
entry.bind("<Control-v>", paste_image)  # Wiązanie Ctrl+V z wklejaniem obrazu

# Przycisk do wysyłania wiadomości
send_button = tk.Button(chat_root, text="Wyślij", command=send_message)
send_button.pack(padx=10, pady=5, side=tk.RIGHT)

# Uruchom WebSocket w osobnym wątku
threading.Thread(target=start_websocket, daemon=True).start()

chat_root.mainloop()