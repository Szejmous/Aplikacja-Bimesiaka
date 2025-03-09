import tkinter as tk
from PIL import Image, ImageTk
import subprocess

root = tk.Tk()
root.title("Obliczenia - Arkadiusz Stachyra - Menu")
root.geometry("400x500")

try:
    logo_image = Image.open("logo.png")
    logo = ImageTk.PhotoImage(logo_image)
    logo_label = tk.Label(root, image=logo)
    logo_label.pack(pady=20)
except FileNotFoundError:
    tk.Label(root, text="Moja Firma", font=("Arial", 20)).pack(pady=20)

def uruchom_ugiecie():
    subprocess.Popen(["python", "ugiecie_belki.py"])

def uruchom_worek_przeszkoda():
    subprocess.Popen(["python", "worek_sniegu_przeszkoda.py"])

def uruchom_worek_dach():
    subprocess.Popen(["python", "worek_sniegu_dach.py"])

def uruchom_wspornik():
    subprocess.Popen(["python", "wspornik.py"])

def uruchom_wyboczenie_ramy():
    subprocess.Popen(["python", "wyboczenie_ramy.py"])

def uruchom_chat():
    subprocess.Popen(["python", "chat.py"])

btn_width = 35
btn1 = tk.Button(root, text="Ugięcie Belki", command=uruchom_ugiecie, width=btn_width, height=2)
btn1.pack(pady=10)

btn2 = tk.Button(root, text="Worek śniegu przy przeszkodzie", command=uruchom_worek_przeszkoda, width=btn_width, height=2)
btn2.pack(pady=10)

btn3 = tk.Button(root, text="Worek śniegu przy dachu przyległym", command=uruchom_worek_dach, width=btn_width, height=2)
btn3.pack(pady=10)

btn4 = tk.Button(root, text="Wymiarowanie krótkiego wspornika", command=uruchom_wspornik, width=btn_width, height=2)
btn4.pack(pady=10)

btn5 = tk.Button(root, text="Współczynnik wyboczenia ramy", command=uruchom_wyboczenie_ramy, width=btn_width, height=2)
btn5.pack(pady=10)

btn_chat = tk.Button(root, text="Chat", command=uruchom_chat, width=10, height=2)
btn_chat.place(relx=0.95, rely=0.95, anchor="se")

root.mainloop()