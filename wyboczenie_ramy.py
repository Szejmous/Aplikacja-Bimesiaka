import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageGrab
import math
from datetime import datetime
import os
import tempfile
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.utils import ImageReader

# Stałe
E = 205000 * 10**6  # Moduł Younga stali [N/m^2]

def calculate_kappa(H, L, I_s, I_b, support_type, rama_przesuwna):
    """Oblicza kappa1 i kappa2 dla górnego i dolnego węzła zgodnie z PN-90/B-03200."""
    H_cm = H * 100  # m na cm
    L_cm = L * 100  # m na cm
    
    K_c = I_s / H_cm  # Sztywność słupa w cm^3
    
    # Oblicz K_o dla górnego węzła (sztywne)
    eta1 = 1.0 if rama_przesuwna == "tak" else 2.0
    K_o1 = eta1 * (I_b / L_cm)  # Sztywność zamocowania górnego węzła
    kappa1 = K_c / (K_c + K_o1) if K_c + K_o1 > 0 else 0
    kappa1 = max(kappa1, 0.3)  # Warunek minimalny z PN-90/B-03200 (Z1-3)
    
    # Oblicz K_o dla dolnego węzła zgodnie z normą
    K_o2 = 0.1 * K_c if support_type == "przegubowe" else K_c
    kappa2 = K_c / (K_c + K_o2) if K_c + K_o2 > 0 else 0
    kappa2 = max(kappa2, 0.3)  # Warunek minimalny z PN-90/B-03200 (Z1-3)
    
    return kappa1, kappa2

def draw_frame(canvas, beam_profile, column_profile, beam_length, column_height, support_type, Iy_Iz_beam, Iy_Iz_column):
    """Rysuje ramę na canvasie na podstawie aktualnych danych."""
    canvas.delete("all")
    canvas_width, canvas_height = 600, 300
    
    margin = 50
    frame_width_cm = beam_length * 100
    frame_height_cm = column_height * 100
    scale_width = (canvas_width - 2 * margin) / frame_width_cm
    scale_height = (canvas_height - 2 * margin - 20) / frame_height_cm
    scale = min(scale_width, scale_height, 1.0)
    
    frame_width = frame_width_cm * scale
    frame_height = frame_height_cm * scale
    beam_x1 = (canvas_width - frame_width) / 2
    beam_x2 = beam_x1 + frame_width
    column_y2 = canvas_height - margin
    beam_y = column_y2 - frame_height
    
    # Rysuj słupy i belkę
    canvas.create_line(beam_x1, beam_y, beam_x1, column_y2, width=2, fill="black")
    canvas.create_line(beam_x2, beam_y, beam_x2, column_y2, width=2, fill="black")
    canvas.create_line(beam_x1, beam_y, beam_x2, beam_y, width=2, fill="black")
    
    # Etykiety profili
    canvas.create_text(beam_x1 - 20, beam_y - 15, text=f"Belka: {beam_profile}", anchor="e", font=("Arial", 8))
    canvas.create_text(beam_x1 - 20, column_y2 + 15, text=f"Slup: {column_profile}", anchor="e", font=("Arial", 8))
    canvas.create_text(beam_x2 + 20, column_y2 + 15, text=f"Slup: {column_profile}", anchor="w", font=("Arial", 8))
    
    # Wymiary
    dim_x1, dim_x2, dim_y = beam_x1, beam_x2, beam_y - 20
    canvas.create_line(dim_x1, dim_y, dim_x2, dim_y, width=1)
    stroke_length = 10
    canvas.create_line(dim_x1 - stroke_length / math.sqrt(2), dim_y - stroke_length / math.sqrt(2),
                       dim_x1 + stroke_length / math.sqrt(2), dim_y + stroke_length / math.sqrt(2),
                       width=2, fill="black")
    canvas.create_line(dim_x2 - stroke_length / math.sqrt(2), dim_y - stroke_length / math.sqrt(2),
                       dim_x2 + stroke_length / math.sqrt(2), dim_y + stroke_length / math.sqrt(2),
                       width=2, fill="black")
    canvas.create_text((dim_x1 + dim_x2) / 2, dim_y - 10, text=f"{beam_length} m", font=("Arial", 8))
    
    dim_y1, dim_y2, dim_x = column_y2, beam_y, beam_x1 - 20
    canvas.create_line(dim_x, dim_y1, dim_x, dim_y2, width=1)
    canvas.create_line(dim_x - stroke_length / math.sqrt(2), dim_y1 - stroke_length / math.sqrt(2),
                       dim_x + stroke_length / math.sqrt(2), dim_y1 + stroke_length / math.sqrt(2),
                       width=2, fill="black")
    canvas.create_line(dim_x - stroke_length / math.sqrt(2), dim_y2 - stroke_length / math.sqrt(2),
                       dim_x + stroke_length / math.sqrt(2), dim_y2 + stroke_length / math.sqrt(2),
                       width=2, fill="black")
    canvas.create_text(dim_x + 15, (dim_y1 + dim_y2) / 2, text=f"{column_height} m", font=("Arial", 8), angle=90)
    
    # Rysuj podpory
    if support_type == "przegubowe":
        canvas.create_polygon(beam_x1 - 10, column_y2, beam_x1 + 10, column_y2, beam_x1, column_y2 - 15, outline="black", fill="")
        canvas.create_polygon(beam_x2 - 10, column_y2, beam_x2 + 10, column_y2, beam_x2, column_y2 - 15, outline="black", fill="")
    else:
        canvas.create_line(beam_x1 - 15, column_y2, beam_x1 + 15, column_y2, width=2, fill="black")
        for i in range(-10, 11, 5):
            canvas.create_line(beam_x1 + i, column_y2, beam_x1 + i - 5, column_y2 + 10, width=1, fill="black")
        canvas.create_line(beam_x2 - 15, column_y2, beam_x2 + 15, column_y2, width=2, fill="black")
        for i in range(-10, 11, 5):
            canvas.create_line(beam_x2 + i, column_y2, beam_x2 + i - 5, column_y2 + 10, width=1, fill="black")

def draw_diagram(canvas, image, kappa1, kappa2, rama_przesuwna, width=400, height=400):
    """Rysuje diagram z liniami pionowymi i poziomymi odpowiadającymi wartościom kappa1 i kappa2 z większą precyzją i ciągłymi liniami, skorygowane pozycje o podane różnice."""
    canvas.delete("all")
    
    # Otwórz i zmień rozmiar obrazu diagramu
    photo = ImageTk.PhotoImage(image.resize((width, height), Image.LANCZOS))
    canvas.create_image(width // 2, height // 2, image=photo)
    
    # Upewnij się, że wartości kappa są w zakresie 0-1
    kappa1 = max(0.0, min(1.0, kappa1))  # Ograniczenie do zakresu 0-1
    kappa2 = max(0.0, min(1.0, kappa2))  # Ograniczenie do zakresu 0-1
    
    # Oblicz pozycje linii z większą precyzją, dostosowana skala dla osi 0-1
    # Oś pozioma (k1): od 0 (lewo) do 1 (prawo)
    # Oś pionowa (k2): od 0 (dół) do 1 (góra)
    
    # Stałe korekty pozycji na podstawie podanych różnic
    if rama_przesuwna == "tak":
        # Dla ramy przesuwnej: koryguj o różnice 0.081 dla k2 i 0.025 dla k1
        corrected_kappa2 = max(0.0, min(1.0, kappa2 - 0.081))  # Korekta dla k2 (0.99 → 0.909)
        corrected_kappa1 = max(0.0, min(1.0, kappa1 - 0.025))  # Korekta dla k1 (0.65 → 0.625)
        x_kappa2 = corrected_kappa2 * width  # Pozycja pionowa dla k2 (0 na lewo, width na prawo)
        y_kappa1 = (1 - corrected_kappa1) * height  # Pozycja pozioma dla k1 (0 na dole, height na górze)
    else:
        # Dla ramy nieprzesuwnej: koryguj o różnice 0.041 dla k2 i 0.030 dla k1
        corrected_kappa2 = max(0.0, min(1.0, kappa2 - 0.041))  # Korekta dla k2 (0.95 → 0.909)
        corrected_kappa1 = max(0.0, min(1.0, kappa1 - 0.030))  # Korekta dla k1 (0.455 → 0.425)
        x_kappa2 = corrected_kappa2 * width  # Pozycja pionowa dla k2 (0 na lewo, width na prawo)
        y_kappa1 = (1 - corrected_kappa1) * height  # Pozycja pozioma dla k1 (0 na dole, height na górze)
    
    # Rysuj ciągłe linie z wyraźniejszymi parametrami (większa grubość)
    canvas.create_line(x_kappa2, 0, x_kappa2, height, fill="red", width=3)  # Linia pionowa ciągła
    canvas.create_line(0, y_kappa1, width, y_kappa1, fill="red", width=3)  # Linia pozioma ciągła
    
    # Zachowaj referencję do obrazu
    canvas.image = photo

def capture_frame_canvas(canvas):
    """Zapisuje zawartość Canvas ramy do pliku PNG poprzez bezpośredni screenshot (używając ImageGrab)."""
    try:
        # Utwórz tymczasowy plik PNG poprzez zrzut ekranu canvasa
        x = canvas.winfo_rootx()
        y = canvas.winfo_rooty()
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        
        # Zrób zrzut ekranu obszaru canvasa używając ImageGrab
        screenshot = ImageGrab.grab(bbox=(x, y, x + width, y + height))
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png', mode='w+b') as temp_png:
            screenshot.save(temp_png, "PNG", dpi=(300, 300))  # Zapis z wyższą rozdzielczością
            temp_png_path = temp_png.name
        
        return temp_png_path
    except Exception as e:
        messagebox.showerror("Błąd", f"Nie można zapisać pliku tymczasowego: {e}")
        return None

def remove_diacritics(text):
    """Zastępuje polskie znaki diakrytyczne ich bazowymi literami łacińskimi."""
    replacements = {
        'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n', 'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z',
        'Ą': 'A', 'Ć': 'C', 'Ę': 'E', 'Ł': 'L', 'Ń': 'N', 'Ó': 'O', 'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z'
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text

def export_to_pdf(kappa1, kappa2, input_data, numer_tematu, nazwa_obliczen, frame_image):
    """Eksportuje wyniki do PDF, zastępując znaki specjalne odpowiednikami ASCII."""
    if not frame_image or not os.path.exists(frame_image):
        messagebox.showerror("Błąd", "Plik obrazu ramy nie istnieje lub nie został podany.")
        return
    
    today = datetime.now()
    filename = f"{numer_tematu}_{nazwa_obliczen}_{today.strftime('%d-%m-%Y')}.pdf"
    save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("Pliki PDF", "*.pdf")], title="Zapisz plik", initialfile=filename)
    if not save_path:
        return

    c = pdf_canvas.Canvas(save_path, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica", 12)

    # Wklej ramę
    try:
        frame_img = ImageReader(frame_image)
        c.drawImage(frame_img, 50, height - 350, width=600, height=300)
    except Exception as e:
        messagebox.showerror("Błąd", f"Nie można wkleić ramy: {e}")
        c.showPage()
        c.save()
        return

    # Wklej diagram
    try:
        diagram_img = ImageReader("przesuwna.png" if "tak" in input_data.get("Czy rama jest przesuwna?", "tak") else "nieprzesuwna.png")
        c.drawImage(diagram_img, 50, height - 700, width=300, height=300)
    except Exception as e:
        messagebox.showerror("Błąd", f"Nie można wkleić diagramu: {e}")
        c.showPage()
        c.save()
        return

    # Tekst z wartościami k1 i k2
    text_y = height - 750
    c.drawString(50, text_y, f"k1 = {kappa1:.3f}")
    text_y -= 20
    c.drawString(50, text_y, f"k2 = {kappa2:.3f}")
    text_y -= 20

    # Dane wejściowe bez diakrytyków
    for key, value in input_data.items():
        key = remove_diacritics(key).replace("κ", "k")
        value = remove_diacritics(str(value)).replace("κ", "k")
        text = f"{key}: {value}"
        c.drawString(50, text_y, text)
        text_y -= 20

    c.showPage()
    c.save()
    if os.path.exists(frame_image):
        os.remove(frame_image)
    messagebox.showinfo("Sukces", "Plik PDF został zapisany pomyślnie!")

def wyboczenie_ramy():
    window = tk.Toplevel()
    window.title("Wspolczynnik wyboczenia ramy")
    
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    window_width = 1200
    window_height = 800
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    with open("przekroje.json", "r") as f:
        profiles = json.load(f)

    support_var = tk.StringVar(value="przegubowe")
    beam_category = tk.StringVar(value="HEA")
    beam_profile = tk.StringVar(value="HEA160")
    column_category = tk.StringVar(value="HEA")
    column_profile = tk.StringVar(value="HEA160")
    Iy_Iz_beam = tk.StringVar(value="Iy")
    Iy_Iz_column = tk.StringVar(value="Iy")
    beam_length = tk.DoubleVar(value=5.0)
    column_height = tk.DoubleVar(value=3.0)
    rama_przesuwna = tk.StringVar(value="tak")

    left_frame = tk.Frame(window)
    left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    right_frame = tk.Frame(window)
    right_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    tk.Label(left_frame, text="Dlugosc belki [m]:").grid(row=0, column=0, padx=5, pady=5)
    tk.Entry(left_frame, textvariable=beam_length).grid(row=0, column=1, padx=5, pady=5)
    tk.Label(left_frame, text="Wysokosc slupa [m]:").grid(row=1, column=0, padx=5, pady=5)
    tk.Entry(left_frame, textvariable=column_height).grid(row=1, column=1, padx=5, pady=5)
    tk.Label(left_frame, text="Typ podpory:").grid(row=2, column=0, padx=5, pady=5)
    tk.Radiobutton(left_frame, text="Przegubowe", variable=support_var, value="przegubowe").grid(row=2, column=1)
    tk.Radiobutton(left_frame, text="Utwierdzenie", variable=support_var, value="utwierdzenie").grid(row=2, column=2)
    tk.Label(left_frame, text="Slup:").grid(row=3, column=0, padx=5, pady=5)
    column_category_combo = ttk.Combobox(left_frame, textvariable=column_category, values=list(profiles.keys()))
    column_category_combo.grid(row=3, column=1)
    column_profile_combo = ttk.Combobox(left_frame, textvariable=column_profile, values=["HEA160"])
    column_profile_combo.grid(row=3, column=2)
    tk.Label(left_frame, text="Os slupa:").grid(row=4, column=0, padx=5, pady=5)
    tk.Radiobutton(left_frame, text="Iy", variable=Iy_Iz_column, value="Iy").grid(row=4, column=1)
    tk.Radiobutton(left_frame, text="Iz", variable=Iy_Iz_column, value="Iz").grid(row=4, column=2)
    tk.Label(left_frame, text="Belka:").grid(row=5, column=0, padx=5, pady=5)
    beam_category_combo = ttk.Combobox(left_frame, textvariable=beam_category, values=list(profiles.keys()))
    beam_category_combo.grid(row=5, column=1)
    beam_profile_combo = ttk.Combobox(left_frame, textvariable=beam_profile, values=["HEA160"])
    beam_profile_combo.grid(row=5, column=2)
    tk.Label(left_frame, text="Os belki:").grid(row=6, column=0, padx=5, pady=5)
    tk.Radiobutton(left_frame, text="Iy", variable=Iy_Iz_beam, value="Iy").grid(row=6, column=1)
    tk.Radiobutton(left_frame, text="Iz", variable=Iy_Iz_beam, value="Iz").grid(row=6, column=2)
    tk.Label(left_frame, text="Czy rama jest przesuwna?").grid(row=7, column=0, padx=5, pady=5)
    tk.Radiobutton(left_frame, text="Tak", variable=rama_przesuwna, value="tak").grid(row=7, column=1)
    tk.Radiobutton(left_frame, text="Nie", variable=rama_przesuwna, value="nie").grid(row=7, column=2)

    tk.Label(left_frame, text="Numer tematu:").grid(row=10, column=0, padx=5, pady=5)
    numer_tematu_var = tk.StringVar(value="B_")
    tk.Entry(left_frame, textvariable=numer_tematu_var).grid(row=10, column=1, padx=5, pady=5)
    
    tk.Label(left_frame, text="Nazwa obliczen:").grid(row=11, column=0, padx=5, pady=5)
    nazwa_obliczen_var = tk.StringVar(value="Obliczenia_Ramy")
    tk.Entry(left_frame, textvariable=nazwa_obliczen_var).grid(row=11, column=1, padx=5, pady=5)

    canvas = tk.Canvas(left_frame, width=600, height=300, bg="white")
    canvas.grid(row=12, column=0, columnspan=2, pady=10)
    
    result_label = tk.Label(left_frame, text="k1 = -\nk2 = -\nOdczytaj mu z diagramu PN-90/B-03200 (Rys. Z1-13 b dla wezlow przesuwnych lub Z1-13 a dla wezlow nieprzesuwnych)", justify="left")
    result_label.grid(row=13, column=0, columnspan=2, pady=10)

    export_button = tk.Button(left_frame, text="Eksportuj do PDF", command=lambda: export_results(
        numer_tematu_var.get(), nazwa_obliczen_var.get(), {
            "Dlugosc belki [m]": beam_length.get(),
            "Wysokosc slupa [m]": column_height.get(),
            "Typ podpory": support_var.get(),
            "Slup": column_profile.get(),
            "Os slupa": Iy_Iz_column.get(),
            "Belka": beam_profile.get(),
            "Os belki": Iy_Iz_beam.get(),
            "Czy rama jest przesuwna?": rama_przesuwna.get()
        }, canvas
    ))
    export_button.grid(row=14, column=0, columnspan=2, pady=5)

    diagram_canvas = tk.Canvas(right_frame, width=400, height=400, bg="white")
    diagram_canvas.pack(pady=10)

    def update_profiles(*args):
        beam_profile_combo['values'] = list(profiles[beam_category.get()].keys())
        beam_profile.set(list(profiles[beam_category.get()].keys())[0])
        column_profile_combo['values'] = list(profiles[column_category.get()].keys())
        column_profile.set(list(profiles[column_category.get()].keys())[0])
        update_frame()

    def update_frame(*args):
        try:
            beam_len = beam_length.get()
            column_h = column_height.get()
            support = support_var.get()
            beam_prof = beam_profile.get()
            column_prof = column_profile.get()
            beam_cat = beam_category.get()
            column_cat = column_category.get()
            przesuwna = rama_przesuwna.get()

            I_b = profiles[beam_cat][beam_prof][Iy_Iz_beam.get()]
            I_s = profiles[column_cat][column_prof][Iy_Iz_column.get()]

            draw_frame(canvas, beam_prof, column_prof, beam_len, column_h, support, Iy_Iz_beam.get(), Iy_Iz_column.get())
            kappa1, kappa2 = calculate_kappa(column_h, beam_len, I_s, I_b, support, przesuwna)
            diagram_note = "(Rys. Z1-13 b dla wezlow przesuwnych)" if przesuwna == "tak" else "(Rys. Z1-13 a dla wezlow nieprzesuwnych)"
            result_label.config(text=f"k1 = {kappa1:.3f}\nk2 = {kappa2:.3f}\nOdczytaj mu z diagramu PN-90/B-03200 {diagram_note}")

            img_path = "przesuwna.png" if przesuwna == "tak" else "nieprzesuwna.png"
            img = Image.open(img_path)
            draw_diagram(diagram_canvas, img, kappa1, kappa2, rama_przesuwna)

        except Exception as e:
            result_label.config(text=f"Błąd: {str(e)}")

    def export_results(numer_tematu, nazwa_obliczen, input_data, canvas):
        try:
            beam_len = beam_length.get()
            column_h = column_height.get()
            support = support_var.get()
            beam_prof = beam_profile.get()
            column_prof = column_profile.get()
            beam_cat = beam_category.get()
            column_cat = column_category.get()
            przesuwna = rama_przesuwna.get()
            I_b = profiles[beam_cat][beam_prof][Iy_Iz_beam.get()]
            I_s = profiles[column_cat][column_prof][Iy_Iz_column.get()]
            kappa1, kappa2 = calculate_kappa(column_h, beam_len, I_s, I_b, support, przesuwna)
            frame_image = capture_frame_canvas(canvas)
            if frame_image:
                export_to_pdf(kappa1, kappa2, input_data, numer_tematu, nazwa_obliczen, frame_image)
                messagebox.showinfo("Sukces", "Plik PDF został zapisany pomyślnie!")
        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd podczas eksportu: {str(e)}")

    beam_length.trace('w', update_frame)
    column_height.trace('w', update_frame)
    support_var.trace('w', update_frame)
    beam_category.trace('w', update_profiles)
    beam_profile.trace('w', update_frame)
    column_category.trace('w', update_profiles)
    column_profile.trace('w', update_frame)
    Iy_Iz_beam.trace('w', update_frame)
    Iy_Iz_column.trace('w', update_frame)
    rama_przesuwna.trace('w', update_frame)

    update_profiles()
    update_frame()
    window.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    wyboczenie_ramy()