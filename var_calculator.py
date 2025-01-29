import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from compute_var import calculate_var


# Función para cargar el portfolio inicial desde un archivo CSV
def cargar_portfolio():
    try:
        df = pd.read_csv("input/portfolio.csv")
        # Verificamos si las columnas esperadas están en el archivo
        expected_columns = {"Ticker", "NumeroAcciones", "Precio", "Divisa"}
        if not expected_columns.issubset(set(df.columns)):
            raise ValueError(
                "El archivo no tiene las columnas requeridas: Ticker, NumeroAcciones, Precio, Divisa"
            )

        for index, row in df.iterrows():
            tree_portfolio.insert(
                "",
                "end",
                values=(
                    row["Ticker"],
                    row["NumeroAcciones"],
                    row["Precio"],
                    row["Divisa"],
                ),
            )
    except FileNotFoundError:
        # Si el archivo no existe, creamos uno de ejemplo
        df = pd.DataFrame(columns=["Ticker", "NumeroAcciones", "Precio", "Divisa"])
        df.to_csv("portfolio.csv", index=False)
        messagebox.showinfo(
            "Archivo creado",
            "No se encontró el archivo portfolio.csv. Se ha creado un archivo vacío como ejemplo.",
        )
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar el archivo: {e}")


# Función para añadir una nueva posición al portfolio temporal
def añadir_posicion():
    ticker = entry_ticker.get()
    num_acciones = entry_num_acciones.get()
    precio = entry_precio.get()
    divisa = combo_divisa.get()

    if not (ticker and num_acciones and precio and divisa):
        messagebox.showerror("Error", "Todos los campos son obligatorios")
        return

    try:
        num_acciones = float(num_acciones)
        precio = float(precio)
        tree_temporal.insert("", "end", values=(ticker, num_acciones, precio, divisa))
        # Limpiar los campos
        entry_ticker.delete(0, tk.END)
        entry_num_acciones.delete(0, tk.END)
        entry_precio.delete(0, tk.END)
        combo_divisa.set("")
    except ValueError:
        messagebox.showerror("Error", "Número de Acciones y Precio deben ser números")


# Función para eliminar una posición de un Treeview
def eliminar_posicion(tree):
    seleccion = tree.selection()
    if seleccion:
        for item in seleccion:
            tree.delete(item)
    else:
        messagebox.showwarning("Advertencia", "Selecciona una posición para eliminar")


# Función para calcular el VaR
def calcular_var():
    shares = []
    num_shares = []
    price_shares = []

    currency_shares = []

    for item in tree_portfolio.get_children():
        valores = tree_portfolio.item(item, "values")
        shares.append(valores[0])
        num_shares.append(float(valores[1]))
        price_shares.append(float(valores[2]))
        currency_shares.append(valores[3])

    # Sumar precios del portfolio temporal
    for item in tree_temporal.get_children():
        valores = tree_temporal.item(item, "values")
        shares.append(valores[0])
        num_shares.append(float(valores[1]))
        price_shares.append(float(valores[2]))
        currency_shares.append(valores[3])

    confidence_level = float(entry_confianza.get()) / 100
    valor_total_quintet = float(entry_valor_quintet.get())
    valor_total_ibkr = float(entry_cantidad_ibkr.get())
    var_ibkr = float(int(entry_ibkr_var.get()))
    # Mostrar el resultado
    var_quintet = calculate_var(
        shares,
        num_shares,
        price_shares,
        currency_shares,
        valor_total_quintet,
        confidence_level,
    )
    var_total = var_quintet + var_ibkr
    messagebox.showinfo(
        "VaR Calculado",
        f"El VaR total es: {var_total :.2f} EUR \n El VaR de quintet es: {var_quintet:.2f} EUR \n El VaR de IBKR es {var_ibkr:.2f} EUR\n El VaR supone un {round(100*var_total/(valor_total_ibkr+valor_total_quintet),3)}% de la cartera total",
    )


# Configuración de la ventana principal
app = tk.Tk()
app.title("Gestor de Portfolio")
app.geometry("900x1000")  # Tamaño inicial más grande

# Sección 1: Tabla del portfolio actual
frame_portfolio = tk.Frame(app)
frame_portfolio.pack(pady=10, fill="both", expand=True)

tk.Label(frame_portfolio, text="Portfolio Actual", font=("Arial", 14)).pack(anchor="w")

columns = ("Ticker", "NumeroAcciones", "Precio", "Divisa")
tree_portfolio = ttk.Treeview(
    frame_portfolio, columns=columns, show="headings", height=8
)
for col in columns:
    tree_portfolio.heading(col, text=col)
    tree_portfolio.column(col, width=100)

tree_portfolio.pack(side="left", fill="both", expand=True)

scrollbar_portfolio = ttk.Scrollbar(
    frame_portfolio, orient="vertical", command=tree_portfolio.yview
)
scrollbar_portfolio.pack(side="right", fill="y")
tree_portfolio.configure(yscrollcommand=scrollbar_portfolio.set)

btn_eliminar_portfolio = tk.Button(
    frame_portfolio,
    text="Eliminar Selección",
    command=lambda: eliminar_posicion(tree_portfolio),
)
btn_eliminar_portfolio.pack(anchor="w", pady=5)

# Sección 2: Tabla de posiciones temporales
frame_temporal = tk.Frame(app)
frame_temporal.pack(pady=10, fill="both", expand=True)

tk.Label(frame_temporal, text="Posiciones Añadidas", font=("Arial", 14)).pack(
    anchor="w"
)

tree_temporal = ttk.Treeview(frame_temporal, columns=columns, show="headings", height=8)
for col in columns:
    tree_temporal.heading(col, text=col)
    tree_temporal.column(col, width=100)

tree_temporal.pack(side="left", fill="both", expand=True)

scrollbar_temporal = ttk.Scrollbar(
    frame_temporal, orient="vertical", command=tree_temporal.yview
)
scrollbar_temporal.pack(side="right", fill="y")
tree_temporal.configure(yscrollcommand=scrollbar_temporal.set)

btn_eliminar_temporal = tk.Button(
    frame_temporal,
    text="Eliminar Selección",
    command=lambda: eliminar_posicion(tree_temporal),
)
btn_eliminar_temporal.pack(anchor="w", pady=5)

# Sección 3: Formulario para añadir posiciones
frame_formulario = tk.Frame(app)
frame_formulario.pack(pady=10, fill="x")

tk.Label(frame_formulario, text="Ticker:").grid(row=0, column=0, padx=5, pady=5)
entry_ticker = tk.Entry(frame_formulario)
entry_ticker.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_formulario, text="Número de Acciones:").grid(
    row=1, column=0, padx=5, pady=5
)
entry_num_acciones = tk.Entry(frame_formulario)
entry_num_acciones.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame_formulario, text="Precio:").grid(row=2, column=0, padx=5, pady=5)
entry_precio = tk.Entry(frame_formulario)
entry_precio.grid(row=2, column=1, padx=5, pady=5)

tk.Label(frame_formulario, text="Divisa:").grid(row=3, column=0, padx=5, pady=5)
combo_divisa = ttk.Combobox(
    frame_formulario,
    values=["USD", "EUR", "GBP", "JPY", "CHF", "AUD", "CAD", "CNY", "SEK", "NZD"],
)
combo_divisa.grid(row=3, column=1, padx=5, pady=5)

btn_añadir = tk.Button(
    frame_formulario, text="Añadir Posición", command=añadir_posicion
)
btn_añadir.grid(row=4, column=0, columnspan=2, pady=10)

# Sección para intervalo de confianza, valor total del portfolio e IBKR VaR

frame_datos_adicionales = tk.Frame(app)
frame_datos_adicionales.pack(pady=20, fill="x")

tk.Label(frame_datos_adicionales, text="Intervalo de Confianza (%):").grid(
    row=0, column=0, padx=5, pady=5, sticky="e"
)
entry_confianza = tk.Entry(frame_datos_adicionales)
entry_confianza.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_datos_adicionales, text="Cantidad total en quintet").grid(
    row=1, column=0, padx=5, pady=5, sticky="e"
)
entry_valor_quintet = tk.Entry(frame_datos_adicionales)
entry_valor_quintet.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame_datos_adicionales, text="Cantidad total en IBKR:").grid(
    row=2, column=0, padx=5, pady=5
)
entry_cantidad_ibkr = tk.Entry(frame_datos_adicionales)
entry_cantidad_ibkr.grid(row=2, column=1, padx=5, pady=5)

tk.Label(frame_datos_adicionales, text="IBKR VaR:").grid(
    row=3, column=0, padx=5, pady=5, sticky="e"
)
entry_ibkr_var = tk.Entry(frame_datos_adicionales)
entry_ibkr_var.grid(row=3, column=1, padx=5, pady=5)

# Botón para calcular el VaR
frame_var = tk.Frame(app)
frame_var.pack(pady=20, fill="x")

btn_calcular_var = tk.Button(
    frame_var,
    text="Calcular VaR",
    font=("Arial", 14),
    bg="#4CAF50",
    fg="white",
    command=calcular_var,
)
btn_calcular_var.pack(
    pady=10, side="bottom", anchor="s"
)  # Aseguramos que esté siempre visible

# Cargar el portfolio inicial
cargar_portfolio()

# Ejecutar la aplicación
app.mainloop()
