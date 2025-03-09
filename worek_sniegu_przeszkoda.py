import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

root = tk.Tk()
root.title("Worek śniegu przy przeszkodzie")
root.geometry("800x600")

canvas = tk.Canvas(root, width=400, height=400, bg="white")
tk.Label(root, text="Funkcjonalność w przygotowaniu – wkrótce dostępna!", font=("Arial", 14)).pack(pady=20)

# Dane dla stref śniegu w Polsce (wg Eurokodu z Aneksem Polskim i mapy)
def oblicz_sk(strefa, A):
    """Oblicza charakterystyczne obciążenie śniegiem sk (kN/m²) na podstawie strefy i wysokości nad poziomem morza."""
    if strefa == "Strefa 1":
        return max(0.007 * A - 1.4, 0.70)  # sk ≥ 0,70 kN/m²
    elif strefa == "Strefa 2":
        return 0.9
    elif strefa == "Strefa 3":
        return max(0.006 * A - 0.6, 1.2)  # sk ≥ 1,2 kN/m²
    elif strefa == "Strefa 4":
        return 1.6
    elif strefa == "Strefa 5":
        return max(0.93 * np.exp(0.00134 * A), 2.0)  # sk ≥ 2,0 kN/m²
    else:
        raise ValueError("Nieprawidłowa strefa śniegu")

# Kształtowe współczynniki μi dla różnych sytuacji (wg Eurokodu)
mu_normal = 1.0      # Normalna sytuacja
mu_sheltered = 1.5   # Osłonięta od wiatru
mu_exposed = 0.8     # Narażona na działanie wiatru

# Współczynniki dla dachów poniżej 20° (typowe dla płaskich dachów)
mu1_flat = 0.8  # Współczynnik kształtu dla dachów płaskich lub o nachyleniu < 20°
Ce_normal = 1.0  # Współczynnik ekspozycji dla terenu normalnego
Ct = 1.0        # Współczynnik termiczny dla dobrze izolowanego dachu

# Współczynniki sezonowości dla śniegu w Polsce (wg EN 1991-1-3 i Aneksu Narodowego)
psi_0 = 0.7  # Dla sytuacji trwałej/przejściowej (persistent/transient)
psi_1 = 0.5  # Dla sytuacji rzadkich (frequent)
psi_2 = 0.2  # Dla sytuacji bardzo rzadkich (quasi-permanent)

def oblicz_Ls(H):
    """Oblicza długość zaspy Ls na podstawie wysokości przeszkody H (wg EN 1991-1-3, Annex B), z granicami 5m i 15m."""
    # Eurocode EN 1991-1-3, Annex B, specifies Ls between 5m and 15m for snow drifts near obstacles
    # For simplicity, use a base value of 5H, but constrain it to 5m–15m
    base_Ls = 5 * H  # Bazowa długość zaspy, ale z ograniczeniami Eurocode
    return max(5.0, min(15.0, base_Ls))  # Ograniczenia: min 5m, max 15m

def oblicz_obciazenie_sniegu(sk, mu, H):
    """Oblicza liniowo zmienne obciążenie śniegu (drift) od maksymalnej wartości do sk, symetryczne po obu stronach."""
    L_s = oblicz_Ls(H)  # Oblicz długość zaspy automatycznie z ograniczeniami 5m–15m
    x = np.linspace(-L_s/2, L_s/2, 100)  # Punkty wzdłuż długości zaspy (symetryczne po obu stronach przeszkody)
    s_max = mu * sk * (1 + 0.8 * (H / 3.0))  # Maksymalne obciążenie proporcjonalne do H (przyjmujemy max. 3m jako referencję)
    s_min = sk  # Podstawowe obciążenie śniegu na końcach zaspy
    s = s_max - (s_max - s_min) * (np.abs(x) / (L_s/2))  # Liniowo zmienne obciążenie, symetryczne, trapezoidalne
    # Obliczenie typowego obciążenia dla dachu < 20° (przykład: 0.72 sk dla strefy 2, normalne warunki)
    s_typical = mu1_flat * Ce_normal * Ct * sk  # Przykład: dla strefy 2, sk = 0.9, s_typical = 0.72 * 0.9 = 0.648 kN/m²
    return x, s, L_s, s_typical

# Zmienne globalne dla widgetów
combo_strefa = None
combo_situacja = None
entry_A = None  # Wysokość nad poziomem morza
entry_H = None  # Wysokość przeszkody

def aktualizuj_wizualizacje(*args):
    global combo_strefa, combo_situacja, entry_A, entry_H
    canvas.delete("all")
    center_x = 200  # Środek canvasu (przeszkoda w środku)
    belka_y = 200
    length_range = 300  # Długość linii (150 po lewej i 150 po prawej od środka)
    
    canvas.create_line(center_x - length_range/2, belka_y, center_x + length_range/2, belka_y, width=4)
    
    try:
        A = float(entry_A.get() or 0)  # Wysokość nad poziomem morza (m)
        H = float(entry_H.get() or 1.0)  # Wysokość przeszkody (domyślnie 1m)
        strefa = combo_strefa.get()
        sk = oblicz_sk(strefa, A)
        sytuacja = combo_situacja.get()
        
        if sytuacja == "Normalna":
            mu = mu_normal
        elif sytuacja == "Osłonięta od wiatru":
            mu = mu_sheltered
        else:  # Narażona na działanie wiatru
            mu = mu_exposed
        
        x, s, L_s, s_typical = oblicz_obciazenie_sniegu(sk, mu, H)
        
        # Wizualizacja przeszkody (prostokąt w środku)
        obstacle_height = min(20, H * 20)  # Skalowanie wysokości przeszkody (maks. 20 px dla czytelności)
        canvas.create_rectangle(center_x - 10, belka_y - obstacle_height, center_x + 10, belka_y, fill="black")
        
        # Wizualizacja obciążenia liniowo zmiennego strzałkami (symetryczne po obu stronach, zielone)
        for i in range(len(x)):
            x_pos = center_x + (x[i] / (L_s/2)) * (length_range/2)
            s_value = s[i] * 1000  # Przelicz na N/m dla wizualizacji
            arrow_length = s_value / 1000  # Skalowanie strzałki (dla czytelności)
            if arrow_length > 0:
                canvas.create_line(x_pos, belka_y, x_pos, belka_y - min(30, arrow_length * 10), arrow=tk.LAST, fill="green")
        
        # Etykiety maksymalnego i podstawowego obciążenia (trapex i obok niego s_typical)
        s_max = mu * sk * (1 + 0.8 * (H / 3.0))
        canvas.create_text(center_x - length_range/2 + 20, belka_y - 50, text=f"{s_max:.2f} kN/m²", font=("Arial", 10))
        canvas.create_text(center_x + length_range/2 - 20, belka_y - 50, text=f"{s_typical:.2f} kN/m²", font=("Arial", 10))
        
        # Wymiary na wykresie (długość zaspy, aktualizowana automatycznie)
        dim_y1 = belka_y + 90
        canvas.create_line(center_x - length_range/2, dim_y1, center_x + length_range/2, dim_y1, width=1)
        canvas.create_line(center_x - length_range/2 - 5, dim_y1-5, center_x - length_range/2 + 5, dim_y1+5, width=2)  # Znak lewy
        canvas.create_line(center_x + length_range/2 - 5, dim_y1-5, center_x + length_range/2 + 5, dim_y1+5, width=2)  # Znak prawy
        canvas.create_text(center_x, dim_y1 + 15, text=f"Ls = {L_s:.2f} m", font=("Arial", 10))
    
    except ValueError:
        canvas.create_text(center_x, belka_y - 50, text="Błąd danych", font=("Arial", 10))

def oblicz_wyniki():
    global combo_strefa, combo_situacja, entry_A, entry_H
    try:
        A = float(entry_A.get() or 0)
        H = float(entry_H.get() or 1.0)
        strefa = combo_strefa.get()
        sk = oblicz_sk(strefa, A)
        sytuacja = combo_situacja.get()
        
        if sytuacja == "Normalna":
            mu = mu_normal
        elif sytuacja == "Osłonięta od wiatru":
            mu = mu_sheltered
        else:  # Narażona na działanie wiatru
            mu = mu_exposed
        
        x, s, L_s, s_typical = oblicz_obciazenie_sniegu(sk, mu, H)
        s_max = mu * sk * (1 + 0.8 * (H / 3.0))  # Maksymalne obciążenie z uwzględnieniem H
        
        # Obliczenie obciążeń z uwzględnieniem współczynników sezonowości
        s_persistent = psi_0 * s_max  # Obciążenie dla sytuacji trwałej/przejściowej
        s_accidental = psi_2 * s_max  # Obciążenie dla sytuacji wyjątkowej (np. zaspy)
        
        # Krok po kroku obliczenia, jak na screenshocie
        calculation_steps = [
            f"1. Teren normalny -> C_t = 1,0",
            f"2. Długość termiczna -> C_e = 1,0",
            f"3. Długość zaspy -> y = h, 2,0 - 0,2m = L_s = {L_s:.2f}m",
            f"4. Współczynnik y+h, sk = {sk:.2f}/200 = {sk/200:.3f}",
            f"Obciążenie charakterystyczne s_t = C_t * C_e * sk = {sk:.2f} * 1,0 * 1,0 = {sk:.2f} kN/m²"
        ]
        
        wyniki_label.config(text="\n".join(calculation_steps) + f"\n\nMaksymalne obciążenie: {s_max:.2f} kN/m²\n"
                                f"Typowe obciążenie dachu < 20°: {s_typical:.2f} kN/m²\n"
                                f"Podstawowe obciążenie gruntu: {sk:.2f} kN/m²\n"
                                f"Obciążenie trwałe/przejściowe: {s_persistent:.2f} kN/m²\n"
                                f"Obciążenie wyjątkowe (zaspy): {s_accidental:.2f} kN/m²\n"
                                f"Wysokość przeszkody H: {H:.2f} m\n"
                                f"Długość zaspy Ls: {L_s:.2f} m", justify="left", fg="black", font=("Arial", 10))
    except ValueError as e:
        wyniki_label.config(text=f"Błąd: {str(e)}", fg="red", font=("Arial", 10))

# Interfejs użytkownika (jak na screenshocie)
input_frame = tk.Frame(root)
input_frame.pack(side=tk.LEFT, padx=10, pady=10)

tk.Label(input_frame, text="Obciążenie charakterystyczne śniegiem gruntu:").pack(pady=5)
combo_strefa = ttk.Combobox(input_frame, values=["Strefa 1", "Strefa 2", "Strefa 3", "Strefa 4", "Strefa 5"])
combo_strefa.set("Strefa 3")  # Domyślnie Strefa 3, jak na screenshocie
combo_strefa.pack()
combo_strefa.bind("<<ComboboxSelected>>", aktualizuj_wizualizacje)

tk.Label(input_frame, text="Wysokość n.p.m. A [m]:").pack(pady=5)
entry_A = tk.Entry(input_frame)
entry_A.insert(0, "0")
entry_A.pack()
entry_A.bind("<KeyRelease>", aktualizuj_wizualizacje)

tk.Label(input_frame, text="Obrys powierzchni narysuj 50 lat:").pack(pady=5)
tk.Checkbutton(input_frame, text="Teren").pack()

tk.Label(input_frame, text="Warunki:").pack(pady=5)
combo_situacja = ttk.Combobox(input_frame, values=["normalne, przepadek", "lokalazyjne, przepadek", "osłonowe, przepadek"])
combo_situacja.set("normalne, przepadek")
combo_situacja.pack()
combo_situacja.bind("<<ComboboxSelected>>", aktualizuj_wizualizacje)

tk.Label(input_frame, text="Sytuacja obciążenia:").pack(pady=5)
combo_situacja2 = ttk.Combobox(input_frame, values=["trwałe/przejściowe, przepadek"])
combo_situacja2.set("trwałe/przejściowe, przepadek")
combo_situacja2.pack()
combo_situacja2.bind("<<ComboboxSelected>>", aktualizuj_wizualizacje)

tk.Label(input_frame, text="Charakterystyka obiektu:").pack(pady=5)
tk.Label(input_frame, text="Wysokość obiektu h [m]:").pack(pady=5)
entry_H = tk.Entry(input_frame)
entry_H.insert(0, "1")
entry_H.pack()
entry_H.bind("<KeyRelease>", aktualizuj_wizualizacje)

tk.Label(input_frame, text="Teren osłonięty obszar przykryty śniegiem:").pack(pady=5)
tk.Checkbutton(input_frame, text="Teren").pack()

tk.Button(input_frame, text="Oblicz wyniki", command=oblicz_wyniki).pack(pady=20)

wyniki_label = tk.Label(input_frame, text="Wyniki pojawią się po obliczeniach", justify="left", fg="black", font=("Arial", 10))
wyniki_label.pack(pady=2)

canvas.pack(side=tk.RIGHT, padx=10, pady=10)
aktualizuj_wizualizacje()

root.mainloop()