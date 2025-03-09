import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

root = tk.Tk()
root.title("Worek śniegu przy dachu przyległym")
root.geometry("800x600")

canvas = tk.Canvas(root, width=400, height=400, bg="white")

tk.Label(root, text="Funkcjonalność w przygotowaniu – wkrótce dostępna!", font=("Arial", 14)).pack(pady=20)

root.mainloop()