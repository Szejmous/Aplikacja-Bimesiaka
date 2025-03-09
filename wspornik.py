import tkinter as tk
from tkinter import messagebox, Toplevel
import math
from PIL import Image, ImageTk

def oblicz_wspornik():
    try:
        # Pobierz dane z pól tekstowych i list rozwijanych na rysunku
        Fv_sd = float(entry_Fv_sd.get())  # kN (B29)
        Hsd_2 = float(entry_Hsd_2.get())  # kN (B32)
        # Beton z listy rozwijanej
        beton = beton_var.get()
        if beton == "C20/25": fck, a_cc = 20, 0.85
        elif beton == "C25/30": fck, a_cc = 25, 0.85
        elif beton == "C30/37": fck, a_cc = 30, 0.85
        elif beton == "C35/45": fck, a_cc = 35, 0.85
        elif beton == "C40/50": fck, a_cc = 40, 0.85
        elif beton == "C45/55": fck, a_cc = 45, 0.85
        elif beton == "C50/60": fck, a_cc = 50, 0.85
        # Stal z przycisków radio
        stal = stal_var.get()
        fyd = 420 if stal == "AIIIN" else 210  # MPa
        fywd = 420 if stal == "AIIIN" else 210  # MPa
        # Średnica zbrojenia z listy rozwijanej
        fw = float(srednica_var.get()) / 1000  # mm -> m
        b = float(entry_b.get())          # m (B43)
        aF = float(entry_aF.get())        # m (B44)
        h = float(entry_h.get())          # m (B45) – użytkownik wprowadza h
        gp = float(entry_gp.get())        # m (B46)
        cw = float(entry_cw.get())        # m (B47)

        # Krok 1: Obciążenia
        Hsd_1 = 0.2 * Fv_sd  # H_sd_1 = 0.2 * F_v,Sd
        Hsd = max(Hsd_1, Hsd_2)  # H_sd = maksimum z H_sd_1 i Hsd_2

        # Krok 2: Dane materiałowe – fcd obliczane wg EC2
        fcd = a_cc * fck / 1.5  # f_cd = α_cc * f_ck / γ_c (γ_c = 1.5 wg EC2)

        # Krok 3: Wymiary geometryczne (formuły z Excela)
        aH = gp + cw + (fw / 2)  # a_H = g_p + c_w + (f_w / 2) [m] (B50)
        d = h - cw - (fw / 2)    # d = h - c_w - (f_w / 2) [m] (B51) – obliczane
        a1 = Fv_sd / (fcd * 1000 * a_cc * b)  # a1 = F_v,Sd / (f_cd * 1000 * a_cc * b) [m] (B52)
        a = aF + aH * Hsd / Fv_sd + 0.5 * a1  # a = a_F + a_H * H_sd / F_v,Sd + 0.5 * a1 [m] (B53)
        a2 = d - math.sqrt((d ** 2) - 2 * a1 * a)  # a2 = d - sqrt(d^2 - 2 * a1 * a) [m] (B54)
        z = d - 0.5 * a2  # z = d - 0.5 * a2 [m] (B55)
        v = 0.6 * (1 - fck / 250)  # v = 0.6 * (1 - f_ck / 250) [-] (B56)
        af_h = aF / h  # a_F / h [m] (B58)

        # Aktualizuj pola tekstowe dla d na rysunku po obliczeniach (h pozostaje edytowalne)
        entry_d.delete(0, tk.END)
        entry_d.insert(0, f"{d:.3f}")
        # entry_h pozostaje bez aktualizacji, bo użytkownik wprowadza h

        # Krok 4: Nośność na ścinanie (FV,Rd)
        FV_Rd = 0  # Inicjalizacja
        if af_h > 0.3:
            FV_Rd = 0.5 * v * fcd * 1000 * a_cc * b * d  # FV_Rd = 0.5 * v * f_cd * 1000 * a_cc * b * d [kN]
        else:
            FV_Rd = 0.4 * v * fcd * 1000 * a_cc * b * d  # FV_Rd = 0.4 * v * f_cd * 1000 * a_cc * b * d [kN]
        FV_Sd = Fv_sd  # FV_Sd = F_v,Sd [kN] (B62)

        # Sprawdzenie warunku
        warunek = "spełniony" if FV_Sd <= FV_Rd else "niespełniony"

        # Krok 5: Wymiarowanie zbrojenia głównego
        As = 0  # Inicjalizacja
        if af_h > 0.3:
            As = ((1 / (fyd * 1000) * (Fv_sd * a / z + Hsd * (aH + z) / z)) * 10000)  # As = [(1/(f_yd*1000)*(F_v,Sd*a/z + H_sd*(a_H+z)/z))*10000] [cm²] (B68)
        else:
            As = (1 / (fyd * 1000) * (0.5 * Fv_sd + Hsd) * 10000)  # As = (1/(f_yd*1000)*(0.5*F_v,Sd + H_sd))*10000 [cm²] (B68)
        Asmin = 0.004 * b * d * 10000  # As_min = 0.004 * b * d * 10000 [cm²] (B72)
        Asrz = max(Asmin, As)  # Główne zbrojenie rzeczywiste = max(As_min, As) [cm²] (B76)

        # Krok 6: Zbrojenie poziome (Asw,h)
        Asw_h = 0  # Inicjalizacja
        if af_h <= 0.3:
            Asw_h = 0.5 * Fv_sd / fywd * 10  # Asw_h = 0.5 * F_v,Sd / f_ywd * 10 [cm²] (B80)
        elif af_h <= 0.6:
            Asw_h = 0.5 * Asrz  # Asw_h = 0.5 * Asrz [cm²] (B80)
        else:
            Asw_h = 0.3 * Asrz  # Asw_h = 0.3 * Asrz [cm²] (B80)

        # Krok 7: Decyzja o zbrojeniu pionowym
        zbrojenie_pionowe = "niewymagane" if af_h <= 0.6 else "wymagane"

        # Krok 8: Zbrojenie pionowe i ścinanie
        ps = Asrz / (b * 100 * d * 100)  # ρ_s = Asrz / (b * 100 * d * 100) (B84)
        k = min(1 + math.sqrt(0.2 / d), 2)  # k = MIN(1 + sqrt(0.2 / d), 2) (B85)
        VRd_ct = 0.12 * k * (100 * ps * fck) ** (1/3) * (2.5 * d / aF) * b * d * 1000  # V_Rd,ct = 0.12 * k * (100 * ρ_s * f_ck)^(1/3) * (2.5 * d / a_F) * b * d * 1000 [kN] (B87)
        FV_Sd_check = Fv_sd  # FV_Sd dla sprawdzenia (B89)

        # Krok 9: Przekrój strzemion pionowych (Asw,v)
        Asw_v = 0  # Inicjalizacja
        if FV_Sd >= VRd_ct:  # Warunek F_v,Sd >= V_Rd,ct
            Asw_v = 0.7 * Fv_sd / (fywd * 0.1)  # 0.7 * F_v,Sd / (f_ywd * 0.1)
        else:
            Asw_v = max(0, ((2 * a / z - 1) / (3 * fywd * 0.1)) * Fv_sd)  # (2 * a / z - 1) / (3 * f_ywd * 0.1) * F_v,Sd, z zabezpieczeniem przed ujemnymi wartościami

        # Aktualizuj pole tekstowe dla As na rysunku po obliczeniach
        entry_As.delete(0, tk.END)
        entry_As.insert(0, f"{Asrz:.2f}")

        # Wyświetl wyniki w nowym oknie od prawej krawędzi, podniesione
        show_results(a_cc, fck, fcd, fyd, fywd, b, gp, fw, Hsd_1, Hsd_2, Hsd, 
                     FV_Rd, FV_Sd, warunek, As, Asmin, Asrz, Asw_h, zbrojenie_pionowe, 
                     ps, k, VRd_ct, FV_Sd_check, Asw_v, 
                     aH, d, a1, a, a2, z, v, af_h)

    except ValueError:
        messagebox.showerror("Błąd", "Wprowadź poprawne wartości liczbowe!")

def show_results(a_cc, fck, fcd, fyd, fywd, b, gp, fw, Hsd_1, Hsd_2, Hsd, 
                 FV_Rd, FV_Sd, warunek, As, Asmin, Asrz, Asw_h, zbrojenie_pionowe, 
                 ps, k, VRd_ct, FV_Sd_check, Asw_v, 
                 aH, d, a1, a, a2, z, v, af_h):
    # Stwórz nowe okno wyników
    result_window = Toplevel(root)
    result_window.title("Wyniki obliczeń wspornika")
    # Oblicz pozycję Y, aby okno było podniesione i widoczne, uwzględniając wysokość ekranu
    screen_height = root.winfo_screenheight()
    root_y = root.winfo_y()
    window_height = 1100
    y_position = max(0, root_y - (window_height - root.winfo_height()) // 2)  # Podnieś okno, ale nie powyżej ekranu
    result_window.geometry(f"400x1100+{root.winfo_x() + root.winfo_width()}+{y_position}")  # Od prawej krawędzi głównego okna, poszerzone w dół do 1100 pikseli, podniesione

    # Utwórz ramkę do wyświetlania wyników
    result_frame = tk.Frame(result_window, bg="white")
    result_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Funkcja do formatowania tekstu z podświetleniem
    def format_text(text, fg=None):  # Zmiana nazwy parametru na 'fg' zamiast 'color'
        label = tk.Label(result_frame, text=text, bg="white", fg="black" if fg is None else fg)
        label.pack(anchor="w")
        return label

    # Dane materiałowe
    format_text("Dane materiałowe:")
    format_text(f"α_cc = {a_cc:.2f} [-]")
    format_text(f"f_ck = {fck:.2f} MPa")
    format_text(f"f_cd = {fcd:.2f} MPa")
    format_text(f"f_yd = {fyd:.2f} MPa")
    format_text(f"f_ywd = {fywd:.2f} MPa")

    # Wymiary geometryczne
    format_text("\nWymiary geometryczne (nie na rysunku):")
    format_text(f"b = {b:.2f} m")
    format_text(f"g_p = {gp:.3f} m")
    format_text(f"f_w = {fw*1000:.0f} mm")  # Przelicz na mm

    # Obciążenia
    format_text("\nObciążenia (nie na rysunku):")
    format_text(f"H_sd_1 = {Hsd_1:.2f} kN")
    format_text(f"H_sd_2 = {Hsd_2:.2f} kN")
    format_text(f"H_sd = {Hsd:.2f} kN")

    # Pośrednie wyniki geometryczne
    format_text("\nPośrednie wyniki geometryczne:")
    format_text(f"a_H = {aH:.3f} m")
    format_text(f"d = {d:.3f} m")
    format_text(f"a1 = {a1:.3f} m")
    format_text(f"a = {a:.3f} m")
    format_text(f"a2 = {a2:.3f} m")
    format_text(f"z = {z:.3f} m")
    format_text(f"v = {v:.3f} [-]")
    format_text(f"a_F/h = {af_h:.3f} [-]")

    # Nośność na ścinanie
    format_text("\nNośność na ścinanie:")
    format_text(f"F_v,Rd = {FV_Rd:.2f} kN")
    format_text(f"F_v,Sd = {FV_Sd:.2f} kN")
    format_text(f"Warunek F_v,Sd ≤ F_v,Rd: {warunek}", 
                fg="green" if warunek == "spełniony" else "red")

    # Wymiarowanie zbrojenia
    format_text("\nWymiarowanie zbrojenia głównego:")
    format_text(f"As (wyliczone) = {As:.2f} cm²", 
                fg="green" if As > Asmin else "black")
    format_text(f"As_min = {Asmin:.2f} cm²")
    format_text(f"As_rz (rzeczywiste) = {Asrz:.2f} cm²", 
                fg="orange" if As <= Asmin else "black")

    format_text("\nZbrojenie poziome:")
    format_text(f"A_sw,h = {Asw_h:.2f} cm²")

    # Zbrojenie pionowe
    format_text("\nZbrojenie pionowe:")
    format_text(f"Zbrojenie pionowe: {zbrojenie_pionowe}", 
                fg="green" if zbrojenie_pionowe == "niewymagane" else "red")
    format_text(f"F_v,Sd = {FV_Sd_check:.2f} kN, V_Rd,ct = {VRd_ct:.2f} kN")  # Faktograficzne wyświetlanie
    format_text(f"A_sw,v = {Asw_v:.2f} cm²", 
                fg="black" if zbrojenie_pionowe == "niewymagane" else "red")
    format_text(f"ρ_s = {ps:.6f} [-]")
    format_text(f"k = {k:.3f} [-]")

    # Ustaw fokus na nowym oknie i uniemożliw interakcję z głównym oknem
    result_window.transient(root)
    result_window.grab_set()

# Okno aplikacji
root = tk.Tk()
root.title("Wymiarowanie krótkiego wspornika")
# Pozycjonowanie okna aplikacji na środku ekranu
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = 900
window_height = 800
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

# Załaduj rysunek jako tło i wyrównaj do prawej krawędzi
try:
    image = Image.open("rysunek_wspornika.png")  # Załóż, że rysunek ma nazwę "rysunek_wspornika.png"
    photo = ImageTk.PhotoImage(image)
    background_label = tk.Label(root, image=photo)
    background_label.image = photo  # Zachowaj referencję
    background_label.place(x=300, y=0, width=600, height=800)  # Wyrównaj rysunek do prawej krawędzi (od x=300)
except FileNotFoundError:
    tk.Label(root, text="Brak rysunku – wstaw rysunek_wspornika.png").pack()

# Ramka dla danych po lewej stronie (szerokość 200 pikseli)
left_frame = tk.Frame(root, width=200, bg="white")
left_frame.pack(side="left", fill="y", padx=5, pady=5)

tk.Label(left_frame, text="Pozostałe dane (wpisz poniżej):", font=("Arial", 12, "bold")).pack(pady=10)

# Lista rozwijana dla betonu
beton_var = tk.StringVar(root)
beton_var.set("C35/45")  # Domyślna wartość
tk.Label(left_frame, text="Klasa betonu", font=("Arial", 10, "bold")).pack(pady=5)
beton_menu = tk.OptionMenu(left_frame, beton_var, "C20/25", "C25/30", "C30/37", "C35/45", "C40/50", "C45/55", "C50/60")
beton_menu.config(font=("Arial", 10, "bold"))
beton_menu.pack(pady=5)

# Przyciski radio dla stali
stal_var = tk.StringVar(root)
stal_var.set("AIIIN")  # Domyślna wartość
tk.Label(left_frame, text="Klasa stali", font=("Arial", 10, "bold")).pack(pady=5)
tk.Radiobutton(left_frame, text="AIIIN (420 MPa)", variable=stal_var, value="AIIIN", font=("Arial", 10, "bold")).pack(pady=2)
tk.Radiobutton(left_frame, text="Inna słabsza (210 MPa)", variable=stal_var, value="Inna słabsza", font=("Arial", 10, "bold")).pack(pady=2)

# Pola dotyczące geometrii (jasnoniebieskie tło, czcionka 10, pogrubiona, żółta ramka)
tk.Label(left_frame, text="Szerokość b [m]", font=("Arial", 10, "bold")).pack(pady=5)
entry_b = tk.Entry(left_frame, bg="#ADD8E6", font=("Arial", 10, "bold"), highlightcolor="yellow", highlightbackground="yellow", highlightthickness=2)
entry_b.pack(pady=5)
entry_b.insert(0, "0.32")

tk.Label(left_frame, text="Grubość podkładki g_p [m]", font=("Arial", 10, "bold")).pack(pady=5)
entry_gp = tk.Entry(left_frame, bg="#ADD8E6", font=("Arial", 10, "bold"), highlightcolor="yellow", highlightbackground="yellow", highlightthickness=2)
entry_gp.pack(pady=5)
entry_gp.insert(0, "0.016")

# Lista rozwijana dla średnicy zbrojenia
srednica_var = tk.StringVar(root)
srednica_var.set("20")  # Domyślna wartość
tk.Label(left_frame, text="Średnica zbrojenia f_w [mm]", font=("Arial", 10, "bold")).pack(pady=5)
srednica_menu = tk.OptionMenu(left_frame, srednica_var, "8", "10", "12", "16", "20", "25", "30")
srednica_menu.config(font=("Arial", 10, "bold"))
srednica_menu.pack(pady=5)

# Pola tekstowe na rysunku (dopasowane do oznaczeń, poszerzone width do 40)
# 1. F_v,Sd – siła pionowa (jasnoczerwone tło, czcionka 10, pogrubiona, żółta ramka)
entry_Fv_sd = tk.Entry(root, width=5, justify="center", bg="#FFA07A", font=("Arial", 10, "bold"), highlightcolor="yellow", highlightbackground="yellow", highlightthickness=2)
entry_Fv_sd.place(x=710, y=210, height=30, width=40)  # Poszerzone width do 40
entry_Fv_sd.insert(0, "442")

# 2. H_sd – siła pozioma (jasnoczerwone tło, czcionka 10, pogrubiona, żółta ramka)
entry_Hsd_2 = tk.Entry(root, width=5, justify="center", bg="#FFA07A", font=("Arial", 10, "bold"), highlightcolor="yellow", highlightbackground="yellow", highlightthickness=2)
entry_Hsd_2.place(x=600, y=230, height=30, width=40)  # Poszerzone width do 40
entry_Hsd_2.insert(0, "0")

# 3. a_F – odległość (jasnoniebieskie tło, czcionka 10, pogrubiona, żółta ramka)
entry_aF = tk.Entry(root, width=5, justify="center", bg="#ADD8E6", font=("Arial", 10, "bold"), highlightcolor="yellow", highlightbackground="yellow", highlightthickness=2)
entry_aF.place(x=600, y=110, height=30, width=40)  # Poszerzone width do 40
entry_aF.insert(0, "0.09")

# 5. h – wysokość (jasnoniebieskie tło, czcionka 10, pogrubiona, żółta ramka, wprowadzane przez użytkownika)
entry_h = tk.Entry(root, width=10, justify="center", bg="#ADD8E6", font=("Arial", 10, "bold"), highlightcolor="yellow", highlightbackground="yellow", highlightthickness=2)
entry_h.place(x=860, y=369, height=30, width=40)  # Poszerzone width do 40, bez aktualizacji po obliczeniach
entry_h.insert(0, "0.6")  # Wartość domyślna (wprowadzana przez użytkownika)

# 6. c_w – otulina (jasnoszare tło, czcionka 10, pogrubiona, żółta ramka)
entry_cw = tk.Entry(root, width=10, justify="center", bg="#D3D3D3", font=("Arial", 10, "bold"), highlightcolor="yellow", highlightbackground="yellow", highlightthickness=2)
entry_cw.place(x=670, y=370, height=30, width=40)  # Poszerzone width do 40
entry_cw.insert(0, "0.07")

# 7. d – wysokość użyteczna (jasnoniebieskie tło, czcionka 10, pogrubiona, bez żółtej ramki, aktualizowane po obliczeniach)
entry_d = tk.Entry(root, width=10, justify="center", bg="#ADD8E6", font=("Arial", 10, "bold"))
entry_d.place(x=777, y=369, height=30, width=40)  # Poszerzone width do 40, aktualizowane po obliczeniach
entry_d.insert(0, "0.52")  # Wartość domyślna (obliczana, może być edytowana przed obliczeniem)

# 7. A_s – zbrojenie (jasnozielone tło, czcionka 10, pogrubiona, bez żółtej ramki, aktualizowane po obliczeniach)
entry_As = tk.Entry(root, width=10, justify="center", bg="#90EE90", font=("Arial", 10, "bold"))
entry_As.place(x=390, y=390, height=30, width=40)  # Poszerzone width do 40
entry_As.insert(0, "7.37")  # Wartość domyślna (może być edytowana przed obliczeniem)

# Przycisk obliczeń (przesunięty na lewą stronę)
tk.Button(left_frame, text="Oblicz", command=oblicz_wspornik).pack(pady=20)

# Funkcja do wyświetlania bieżących współrzędnych kursora (globalne współrzędne)
def show_mouse_position(event):
    # Pobierz globalne współrzędne kursora względem okna root
    x = root.winfo_pointerx() - root.winfo_rootx()
    y = root.winfo_pointery() - root.winfo_rooty()
    position_label.config(text=f"X: {x}, Y: {y}")

# Etykieta do wyświetlania pozycji kursora
position_label = tk.Label(root, text="X: 0, Y: 0", bg="white", fg="black")
position_label.pack(side="bottom", anchor="se", padx=5, pady=5)

# Powiązanie ruchu myszy z funkcją wyświetlającą współrzędne
root.bind("<Motion>", show_mouse_position)

root.mainloop()