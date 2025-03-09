import tkinter as tk
from tkinter import ttk
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Wczytywanie danych z pliku JSON
with open("przekroje.json", "r", encoding="utf-8") as file:
    przekroje = json.load(file)

kategorie = list(przekroje.keys())
warunki_ugiecia = ["L/150", "L/200", "L/250", "L/300", "L/500"]
E_default = 210e9  # Moduł Younga (Pa)
sigma_dop = 355    # Dopuszczalne naprężenie dla S355 (MPa)

root = tk.Tk()
canvas = tk.Canvas(root, width=400, height=400, bg="white")

def aktualizuj_rozmiary(*args):
    kategoria = combo_kategoria.get()
    lista_rozmiarow = list(przekroje[kategoria].keys())
    combo_rozmiar.configure(values=lista_rozmiarow)
    if lista_rozmiarow:
        combo_rozmiar.set(lista_rozmiarow[0] if args else "IPE 200")
    aktualizuj_wizualizacje()

def aktualizuj_wizualizacje(*args):
    canvas.delete("all")
    belka_x_start = 50
    belka_x_end = 350
    belka_y = 200
    belka_length_px = belka_x_end - belka_x_start
    
    canvas.create_line(belka_x_start, belka_y, belka_x_end, belka_y, width=4)
    
    try:
        L = float(entry_L.get() or 0)
        q = float(entry_q.get() or 0)
        P = float(entry_P.get() or 0)
        a = float(entry_a.get() or 0)
    except ValueError:
        L, q, P, a = 0, 0, 0, 0
    
    if tryb.get() == "wolna":
        canvas.create_polygon(belka_x_start-10, belka_y+10, belka_x_start+10, belka_y+10, belka_x_start, belka_y, fill="black")
        canvas.create_polygon(belka_x_end-10, belka_y+10, belka_x_end+10, belka_y+10, belka_x_end, belka_y, fill="black")
        if L > 0:
            Va = q * L / 2 + P * (L - a) / L if P > 0 else q * L / 2
            Vb = q * L / 2 + P * a / L if P > 0 else q * L / 2
            canvas.create_line(belka_x_start, belka_y+40, belka_x_start, belka_y, arrow=tk.FIRST, width=2)
            canvas.create_text(belka_x_start, belka_y+60, text=f"Va={Va:.2f} kN", font=("Arial", 8))
            canvas.create_line(belka_x_end, belka_y+40, belka_x_end, belka_y, arrow=tk.FIRST, width=2)
            canvas.create_text(belka_x_end, belka_y+60, text=f"Vb={Vb:.2f} kN", font=("Arial", 8))
    else:
        canvas.create_line(belka_x_start, belka_y-20, belka_x_start, belka_y+20, width=3)
        canvas.create_line(belka_x_start-10, belka_y-15, belka_x_start, belka_y-5, width=2)
        canvas.create_line(belka_x_start-10, belka_y+15, belka_x_start, belka_y+5, width=2)
        canvas.create_line(belka_x_start-15, belka_y-10, belka_x_start, belka_y, width=2)
        canvas.create_line(belka_x_start-15, belka_y+10, belka_x_start, belka_y, width=2)
        if L > 0:
            Va = q * L + P
            Ma = q * L**2 / 2 + P * a
            canvas.create_line(belka_x_start, belka_y+40, belka_x_start, belka_y, arrow=tk.FIRST, width=2)
            canvas.create_text(belka_x_start, belka_y+60, text=f"Va={Va:.2f} kN", font=("Arial", 8))
            canvas.create_text(belka_x_start+40, belka_y+40, text=f"Ma={Ma:.2f} kNm", font=("Arial", 8))
    
    if q > 0:
        arrow_tops = []
        for i in range(10):
            x = belka_x_start + (i + 0.5) * belka_length_px / 10
            canvas.create_line(x, belka_y-30, x, belka_y, arrow=tk.LAST)
            arrow_tops.append((x, belka_y-30))
        for i in range(len(arrow_tops)-1):
            canvas.create_line(arrow_tops[i], arrow_tops[i+1], width=1)
        canvas.create_text(belka_x_start + belka_length_px/2, belka_y-50, text=f"{q} kN/m", font=("Arial", 10))
    
    if P > 0 and L > 0 and a <= L:
        x_pos = belka_x_start + (a / L) * belka_length_px
        canvas.create_line(x_pos, belka_y-70, x_pos, belka_y, arrow=tk.LAST, width=2)
        canvas.create_text(x_pos, belka_y-90, text=f"{P} kN", font=("Arial", 10))
    
    kategoria = combo_kategoria.get()
    rozmiar = combo_rozmiar.get()
    profil = f"{rozmiar}"
    canvas.create_text(belka_x_start + belka_length_px/2, belka_y+30, text=profil, font=("Arial", 12))
    
    dim_y1 = belka_y + 90
    dim_y2 = belka_y + 120
    
    def rysuj_znak(x, y, kierunek="lewo"):
        if kierunek == "lewo":
            canvas.create_line(x, y-5, x+10, y+5, width=2)
        else:
            canvas.create_line(x-10, y-5, x, y+5, width=2)
    
    if P > 0 and L > 0 and a <= L:
        x_pos = belka_x_start + (a / L) * belka_length_px
        canvas.create_line(belka_x_start, dim_y1, x_pos, dim_y1, width=1)
        rysuj_znak(belka_x_start, dim_y1, "lewo")
        rysuj_znak(x_pos, dim_y1, "prawo")
        canvas.create_text((belka_x_start + x_pos)/2, dim_y1-10, text=f"{a:.2f} m", font=("Arial", 8))
        
        canvas.create_line(x_pos, dim_y1, belka_x_end, dim_y1, width=1)
        rysuj_znak(x_pos, dim_y1, "lewo")
        rysuj_znak(belka_x_end, dim_y1, "prawo")
        canvas.create_text((x_pos + belka_x_end)/2, dim_y1-10, text=f"{L-a:.2f} m", font=("Arial", 8))
        
        canvas.create_line(belka_x_start, dim_y2, belka_x_end, dim_y2, width=1)
        rysuj_znak(belka_x_start, dim_y2, "lewo")
        rysuj_znak(belka_x_end, dim_y2, "prawo")
        canvas.create_text(belka_x_start + belka_length_px/2, dim_y2+15, text=f"L = {L:.2f} m", font=("Arial", 10))
    else:
        canvas.create_line(belka_x_start, dim_y2, belka_x_end, dim_y2, width=1)
        rysuj_znak(belka_x_start, dim_y2, "lewo")
        rysuj_znak(belka_x_end, dim_y2, "prawo")
        canvas.create_text(belka_x_start + belka_length_px/2, dim_y2+15, text=f"L = {L:.2f} m", font=("Arial", 10))

def oblicz_ugiecie_w_punkcie(x, L, q, P, a, E, I, tryb):
    v_q = 0
    v_P = 0
    if tryb == "wolna":
        if q != 0:
            v_q = -(q * x * (L**3 - 2 * L * x**2 + x**3)) / (24 * E * I)
        if P != 0 and 0 <= a <= L:
            b = L - a
            if x <= a:
                v_P = -(P * b * x * (L**2 - b**2 - x**2)) / (6 * E * I * L)
            else:
                v_P = -(P * a * (L - x) * (L**2 - a**2 - (L - x)**2)) / (6 * E * I * L)
    else:
        if q != 0:
            v_q = -(q * x**2 * (6 * L**2 - 4 * L * x + x**2)) / (24 * E * I)
        if P != 0 and 0 <= a <= L:
            if x <= a:
                v_P = -(P * a**2 * (3 * x - a)) / (6 * E * I)
            else:
                v_P = -(P * x**2 * (3 * a - x)) / (6 * E * I)
    return v_q + v_P

def oblicz_moment_w_punkcie(x, L, q, P, a, tryb):
    if tryb == "wolna":
        M_q = q * x * (L - x) / 2 if q != 0 else 0
        M_P = P * (L - a) * x / L if P != 0 and x <= a <= L else P * a * (L - x) / L if P != 0 and a < x <= L else 0
        return -(M_q + M_P) / 1000
    else:
        M_q = q * (L - x)**2 / 2 if q != 0 else 0
        M_P = P * (a - x) if P != 0 and x <= a <= L else 0
        return -(M_q + M_P) / 1000

def oblicz_ugiecie():
    try:
        L = float(entry_L.get())
        q = float(entry_q.get()) * 1000  # N/m
        P = float(entry_P.get()) * 1000  # N
        a = float(entry_a.get())
        E = float(entry_E.get()) * 1e9   # Pa
        
        kategoria = combo_kategoria.get()
        rozmiar = combo_rozmiar.get()
        if os_choice.get() == "Iy":
            I = przekroje[kategoria][rozmiar]["Iy"] * 1e-8
            dim = przekroje[kategoria][rozmiar]["h"] / 1000
        else:
            I = przekroje[kategoria][rozmiar]["Iz"] * 1e-8
            dim = przekroje[kategoria][rozmiar]["b"] / 1000
        
        x_vals = np.linspace(0, L, 201)
        v_vals = [oblicz_ugiecie_w_punkcie(x, L, q, P, a, E, I, tryb.get()) * 1000 for x in x_vals]
        m_vals = [oblicz_moment_w_punkcie(x, L, q, P, a, tryb.get()) for x in x_vals]
        
        V_max = min(v_vals)
        V_min = max(v_vals)
        x_v_max_idx = np.argmin(v_vals)
        x_v_min_idx = np.argmax(v_vals)
        x_v_max = x_vals[x_v_max_idx]
        x_v_min = x_vals[x_v_min_idx]
        
        M_max = abs(min(m_vals))
        x_m_max_idx = np.argmin(m_vals)
        x_m_max = x_vals[x_m_max_idx]
        
        v_at_P = oblicz_ugiecie_w_punkcie(a, L, q, P, a, E, I, tryb.get()) * 1000 if P > 0 and 0 <= a <= L else 0
        v_total = abs(V_max)
        
        if tryb.get() == "wolna":
            M_q = q * L**2 / 8 / 1000
            M_P = P * a * (L - a) / L / 1000 if P != 0 and 0 <= a <= L else 0
        else:
            M_q = q * L**2 / 2 / 1000
            M_P = P * a / 1000 if P != 0 and 0 <= a <= L else 0
        
        warunek = combo_warunek.get()
        denominator = int(warunek.split("/")[1])
        v_dopuszczalne = L / denominator
        
        v_total_mm = round(abs(V_max))
        stosunek_str = f"L/{int(round(L / (abs(V_max) / 1000)))}" if V_max != 0 else "L/∞"
        
        W = I / (dim / 2)
        M_dop = sigma_dop * 1e6 * W / 1e3
        sigma_max = M_max * 1e3 / W / 1e6
        wytężenie = (sigma_max / sigma_dop) * 100
        
        color = "green" if v_total_mm < round(v_dopuszczalne * 1000) else "red"
        wykres_color = "green" if v_total_mm < round(v_dopuszczalne * 1000) else "red"
        
        rzeczywiste_label.config(text=f"Rzeczywiste ugięcie: {v_total_mm} mm ({stosunek_str})", fg=color, font=("Arial", 10, "bold"))
        dopuszczalne_label.config(text=f"Dopuszczalne ugięcie: {round(v_dopuszczalne * 1000)} mm ({warunek})", fg="black")
        moment_label.config(text=f"Maksymalny moment: {M_max:.2f} kNm", fg="purple", font=("Arial", 10, "bold"))
        wytężenie_label.config(text=f"Wytężenie przekroju: {wytężenie:.2f}%", fg="black")

        # Analiza profili w tej samej kategorii (zakres zmieniony na 0.1-1.0)
        profile = przekroje[kategoria]
        v_dop_mm = v_dopuszczalne * 1000
        najlepsze_wykorzystanie = 0
        najlepszy_profil = None
        najgorsze_wykorzystanie = float('inf')
        najgorszy_profil = None

        for profil, dane in profile.items():
            I_prof = dane["Iy"] * 1e-8 if os_choice.get() == "Iy" else dane["Iz"] * 1e-8
            v_vals_prof = [oblicz_ugiecie_w_punkcie(x, L, q, P, a, E, I_prof, tryb.get()) * 1000 for x in x_vals]
            v_max_prof = abs(min(v_vals_prof))
            wykorzystanie = v_max_prof / v_dop_mm if v_dop_mm != 0 else 0

            if 0.1 <= wykorzystanie <= 1.0 and wykorzystanie > najlepsze_wykorzystanie:
                najlepsze_wykorzystanie = wykorzystanie
                najlepszy_profil = profil

            if wykorzystanie > 1.0 and wykorzystanie < najgorsze_wykorzystanie:
                najgorsze_wykorzystanie = wykorzystanie
                najgorszy_profil = profil

        if najlepszy_profil:
            optymalny_label.config(text=f"Najlepszy profil: {najlepszy_profil} ({najlepsze_wykorzystanie:.2%})", fg="green")
        else:
            optymalny_label.config(text="Brak profilu w zakresie 0.1–1.0", fg="black")

        if najgorszy_profil and najgorsze_wykorzystanie != float('inf'):
            przekroczony_label.config(text=f"Pierwszy przekroczony: {najgorszy_profil} ({najgorsze_wykorzystanie:.2%})", fg="red")
        else:
            przekroczony_label.config(text="Brak profilu powyżej 1.0", fg="black")
        
        # Wykresy
        wykres_okno = tk.Toplevel(root)
        wykres_okno.title("Wykresy ugięcia i momentów")
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6, 8), sharex=True)
        
        ax1.plot(x_vals, v_vals, label="Ugięcie (mm)", color=wykres_color)
        ax1.axhline(-v_dopuszczalne * 1000, color="red", linestyle="--", label=f"Dop. ugięcie ({warunek})")
        ax1.axhline(0, color="black", linewidth=0.5)
        ax1.plot(x_v_max, V_max, 'o', color='blue', markersize=8, label=f"Max ugięcie: {V_max:.2f} mm")
        if P > 0 and 0 <= a <= L:
            ax1.plot(a, v_at_P, 'o', color='green', markersize=8, label=f"Ugięcie P: {v_at_P:.2f} mm")
        
        ylim = ax1.get_ylim()
        y_pos = ylim[1] * 0.95
        ax1.text(x_v_max, y_pos, f"{x_v_max:.2f}", ha="center", va="top", color="blue", fontsize=8)
        if P > 0 and 0 <= a <= L:
            ax1.text(a, y_pos, f"{a:.2f}", ha="center", va="top", color="green", fontsize=8)
        
        ax1.text(x_v_min, V_min, f"{V_min:.2f} mm", ha="center", va="bottom", color="blue")
        ax1.set_ylabel("Ugięcie [mm]")
        ax1.set_title(f"Wykres ugięcia dla {rozmiar}")
        ax1.grid(True)
        ax1.legend()
        
        ax2.plot(x_vals, m_vals, label="Moment (kNm)", color="blue")
        ax2.axhline(0, color="black", linewidth=0.5)
        ax2.text(x_m_max, min(m_vals), f"{min(m_vals):.2f} kNm", ha="center", va="top", color="purple")
        if P > 0 and 0 <= a <= L:
            m_at_P = oblicz_moment_w_punkcie(a, L, q, P, a, tryb.get())
            ax2.text(a, m_at_P, f"{m_at_P:.2f} kNm", ha="center", va="bottom" if m_at_P < 0 else "top", color="green")
        ax2.set_xlabel("Położenie x [m]")
        ax2.set_ylabel("Moment [kNm]")
        ax2.set_title("Wykres momentów zginających")
        ax2.grid(True)
        ax2.legend()
        
        if tryb.get() == "wolna":
            ax2.text(L/2, -M_q, f"{-M_q:.2f} kNm", ha="center", va="top")
        else:
            ax2.text(L, 0, "0 kNm", ha="center", va="top")
        
        canvas_wykres = FigureCanvasTkAgg(fig, master=wykres_okno)
        canvas_wykres.draw()
        canvas_wykres.get_tk_widget().pack()

        root.update_idletasks()
        root_x = root.winfo_x()
        root_y = root.winfo_y()
        root_width = root.winfo_width()
        wykres_okno.geometry(f"+{root_x + root_width + 10}+{root_y}")
    except ValueError as e:
        rzeczywiste_label.config(text=f"Błąd: {str(e)}", fg="black", font=("Arial", 10, "bold"))
        dopuszczalne_label.config(text="Dopuszczalne ugięcie: -", fg="black")
        moment_label.config(text="Maksymalny moment: -", fg="purple", font=("Arial", 10, "bold"))
        wytężenie_label.config(text="Wytężenie przekroju: -", fg="black")
        optymalny_label.config(text="Najlepszy profil: -", fg="black")
        przekroczony_label.config(text="Pierwszy przekroczony: -", fg="black")

root.title("Obliczanie ugięcia belki")
root.geometry("800x850")

root.update_idletasks()
width = root.winfo_width()
height = root.winfo_height()
x = (root.winfo_screenwidth() // 2) - (width // 2) - 200
y = (root.winfo_screenheight() // 2) - (height // 2)
root.geometry(f"{width}x{height}+{x}+{y}")

tryb_frame = tk.Frame(root)
tryb_frame.pack(side=tk.TOP, pady=10)
tryb = tk.StringVar(value="wolna")
tk.Radiobutton(tryb_frame, text="Belka swobodnie podparta", variable=tryb, value="wolna", command=aktualizuj_wizualizacje).pack(side=tk.LEFT, padx=10)
tk.Radiobutton(tryb_frame, text="Wspornik", variable=tryb, value="wspornik", command=aktualizuj_wizualizacje).pack(side=tk.LEFT, padx=10)

input_frame = tk.Frame(root)
input_frame.pack(side=tk.LEFT, padx=10, pady=10)

tk.Label(input_frame, text="Długość belki L [m]:").pack(pady=5)
entry_L = tk.Entry(input_frame)
entry_L.insert(0, "2")
entry_L.pack()
entry_L.bind("<KeyRelease>", aktualizuj_wizualizacje)

tk.Label(input_frame, text="Obciążenie równomierne q [kN/m]:").pack(pady=5)
entry_q = tk.Entry(input_frame)
entry_q.insert(0, "5")
entry_q.pack()
entry_q.bind("<KeyRelease>", aktualizuj_wizualizacje)

tk.Label(input_frame, text="Siła skupiona P [kN]:").pack(pady=5)
entry_P = tk.Entry(input_frame)
entry_P.insert(0, "100")
entry_P.pack()
entry_P.bind("<KeyRelease>", aktualizuj_wizualizacje)

tk.Label(input_frame, text="Położenie siły a [m]:").pack(pady=5)
entry_a = tk.Entry(input_frame)
entry_a.insert(0, "0.5")
entry_a.pack()
entry_a.bind("<KeyRelease>", aktualizuj_wizualizacje)

tk.Label(input_frame, text="Moduł Younga E [GPa]:").pack(pady=5)
entry_E = tk.Entry(input_frame)
entry_E.insert(0, "210")
entry_E.pack()

tk.Label(input_frame, text="Wybierz kategorię przekroju:").pack(pady=5)
combo_kategoria = ttk.Combobox(input_frame, values=kategorie)
combo_kategoria.set("IPE")
combo_kategoria.pack()
combo_kategoria.bind("<<ComboboxSelected>>", aktualizuj_rozmiary)

tk.Label(input_frame, text="Wybierz rozmiar przekroju:").pack(pady=5)
combo_rozmiar = ttk.Combobox(input_frame)
combo_rozmiar.pack()
combo_rozmiar.bind("<<ComboboxSelected>>", aktualizuj_wizualizacje)
aktualizuj_rozmiary()

tk.Label(input_frame, text="Wybierz oś ugięcia:").pack(pady=5)
os_choice = tk.StringVar(value="Iy")
tk.Radiobutton(input_frame, text="Oś Y (Iy)", variable=os_choice, value="Iy").pack()
tk.Radiobutton(input_frame, text="Oś Z (Iz)", variable=os_choice, value="Iz").pack()

tk.Label(input_frame, text="Wybierz warunek ugięcia:").pack(pady=5)
combo_warunek = ttk.Combobox(input_frame, values=warunki_ugiecia)
combo_warunek.set("L/250")
combo_warunek.pack()

tk.Button(input_frame, text="Oblicz ugięcie", command=oblicz_ugiecie).pack(pady=20)

rzeczywiste_label = tk.Label(input_frame, text="Rzeczywiste ugięcie: -", justify="left", fg="blue", font=("Arial", 10, "bold"))
rzeczywiste_label.pack(pady=2)
dopuszczalne_label = tk.Label(input_frame, text="Dopuszczalne ugięcie: -", justify="left", fg="black")
dopuszczalne_label.pack(pady=2)
moment_label = tk.Label(input_frame, text="Maksymalny moment: -", justify="left", fg="purple", font=("Arial", 10, "bold"))
moment_label.pack(pady=2)
wytężenie_label = tk.Label(input_frame, text="Wytężenie przekroju: -", justify="left", fg="black")
wytężenie_label.pack(pady=2)
optymalny_label = tk.Label(input_frame, text="Najlepszy profil: -", justify="left", fg="black")
optymalny_label.pack(pady=2)
przekroczony_label = tk.Label(input_frame, text="Pierwszy przekroczony: -", justify="left", fg="black")
przekroczony_label.pack(pady=2)

canvas.pack(side=tk.RIGHT, padx=10, pady=10)
aktualizuj_wizualizacje()

root.mainloop()