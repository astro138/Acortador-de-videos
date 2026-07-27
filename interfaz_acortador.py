# By: Alan Lobos Román
# Versión: 3.0 - Arquitectura Modular y UI Avanzada
# Fecha: Julio 2026
# Descripción: 
# Módulo de Interfaz Gráfica (GUI) usando Tkinter. Maneja el 
# flujo visual: Selección, Confirmación, Pantalla de Carga 
# con cronómetro y procesamiento en segundo plano (Threading).

import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import threading

def crear_interfaz(comando_analizar, comando_procesar):
    # Configuración de la ventana principal
    root = tk.Tk()
    root.title("Acortador de Videos para WhatsApp - Alan Lobos Román")
    root.geometry("550x250")
    root.config(padx=20, pady=20)
    
    # Variables de estado
    ruta_archivo = tk.StringVar(value="Ningún archivo seleccionado")
    ruta_salida = tk.StringVar(value="Por defecto (carpeta 'partes_nombrevideo')")
    limite_mb = tk.StringVar(value="63") # Límite por defecto para WhatsApp
    
    def seleccionar_archivo():
        """Abre el explorador para elegir el archivo de video."""
        ruta = filedialog.askopenfilename(title="Seleccionar Video", filetypes=[("Archivos MP4", "*.mp4")])
        if ruta:
            ruta_archivo.set(ruta)

    def seleccionar_carpeta():
        """Abre el explorador para elegir una carpeta de salida manual."""
        ruta = filedialog.askdirectory(title="Seleccionar Carpeta")
        if ruta:
            ruta_salida.set(ruta)

    def formatear_tiempo(segundos_totales):
        """Formatea los segundos a un texto amigable para el usuario."""
        horas = int(segundos_totales // 3600)
        minutos = int((segundos_totales % 3600) // 60)
        segundos = int(segundos_totales % 60)
        
        texto = []
        if horas > 0: texto.append(f"{horas} horas")
        if minutos > 0: texto.append(f"{minutos} min")
        texto.append(f"{segundos} seg")
        return ", ".join(texto)

    # ==========================================
    # PASO 1: ACEPTAR Y ANALIZAR (Validaciones)
    # ==========================================
    def iniciar_proceso():
        archivo = ruta_archivo.get()
        limite = limite_mb.get()
        
        if archivo == "Ningún archivo seleccionado":
            messagebox.showwarning("Atención", "Selecciona un video primero.")
            return
        if not limite.isdigit():
            messagebox.showwarning("Atención", "El límite debe ser numérico.")
            return

        # Ocultamos la ventana principal momentáneamente
        root.withdraw() 
        
        try:
            # Calculamos las particiones estimadas
            partes, tiempo_segundos = comando_analizar(archivo, int(limite))
            
            # Validación: Si el video ya pesa menos que el límite, evitamos renderizar
            if partes == 1:
                messagebox.showinfo("Información", f"El video ya pesa menos del límite de {limite} MB.\nNo es necesario cortarlo.")
                root.deiconify() # Restaurar ventana
                return
            
            tiempo_texto = formatear_tiempo(tiempo_segundos)
            # Pasamos a la siguiente ventana
            mostrar_pantalla_confirmacion(archivo, limite, ruta_salida.get(), partes, tiempo_texto)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el video:\n{e}")
            root.deiconify()

    # ==========================================
    # PASO 2: PANTALLA DE CONFIRMACIÓN
    # ==========================================
    def mostrar_pantalla_confirmacion(archivo, limite, carpeta, partes, tiempo_texto):
        ventana_check = tk.Toplevel(root)
        ventana_check.title("Confirmación")
        ventana_check.geometry("400x180")
        ventana_check.config(padx=20, pady=20)
        ventana_check.grab_set() # Bloquea interacción con otras ventanas
        
        mensaje = f"Se dividirá en {partes} partes.\n\nTiempo estimado: {tiempo_texto}.\n\n¿Desea continuar?"
        tk.Label(ventana_check, text=mensaje, font=("Arial", 11), justify="center").pack(pady=10)
        
        frame_btn = tk.Frame(ventana_check)
        frame_btn.pack(pady=10)
        
        def si_continuar():
            ventana_check.destroy()
            mostrar_pantalla_carga(archivo, limite, carpeta)
            
        def no_continuar():
            ventana_check.destroy()
            root.deiconify() # Cancela y vuelve a la pantalla principal

        tk.Button(frame_btn, text="Sí, continuar", command=si_continuar, bg="#4CAF50", fg="white", width=12).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_btn, text="Cancelar", command=no_continuar, bg="#f44336", fg="white", width=12).pack(side=tk.RIGHT, padx=10)

    # ==========================================
    # PASO 3: PANTALLA DE CARGA CON CRONÓMETRO
    # ==========================================
    def mostrar_pantalla_carga(archivo, limite, carpeta):
        ventana_carga = tk.Toplevel(root)
        ventana_carga.title("Procesando...")
        ventana_carga.geometry("350x180")
        ventana_carga.config(padx=20, pady=20)
        ventana_carga.protocol("WM_DELETE_WINDOW", lambda: None) # Desactiva el botón [X] de cerrar
        
        lbl_texto = tk.Label(ventana_carga, text="Preparando...", font=("Arial", 11, "bold"))
        lbl_texto.pack(pady=5)
        
        lbl_tiempo = tk.Label(ventana_carga, text="Tiempo: 0 seg", font=("Arial", 10))
        lbl_tiempo.pack(pady=5)
        
        # Barra visual de actividad
        barra = ttk.Progressbar(ventana_carga, orient="horizontal", mode='indeterminate', length=280)
        barra.pack(fill=tk.X, pady=10)
        barra.start(15)

        # Control del reloj
        estado_reloj = {"segundos": 0, "corriendo": True}

        def actualizar_reloj():
            if estado_reloj["corriendo"]:
                lbl_tiempo.config(text=f"Tiempo actual: {estado_reloj['segundos']} seg")
                estado_reloj["segundos"] += 1
                ventana_carga.after(1000, actualizar_reloj) 

        def actualizar_texto(parte_actual, total_partes):
            """Callback invocado desde logica.py al cambiar de partición."""
            lbl_texto.config(text=f"Partición {parte_actual} de {total_partes} procesando...")
            estado_reloj["segundos"] = 0 # Reiniciar contador a 0 en nueva partición

        actualizar_reloj() 

        def tarea_fondo():
            """Procesa el video en un hilo paralelo para no congelar la GUI."""
            try:
                comando_procesar(archivo, int(limite), carpeta, 
                               lambda p, t: root.after(0, actualizar_texto, p, t))
                estado_reloj["corriendo"] = False 
                root.after(0, lambda: exito(ventana_carga))
            except Exception as e:
                estado_reloj["corriendo"] = False 
                root.after(0, lambda: error(ventana_carga, str(e)))

        # Inicia el procesamiento en segundo plano
        threading.Thread(target=tarea_fondo, daemon=True).start()

    # ==========================================
    # PASO 4: FINALIZACIÓN Y REINICIO
    # ==========================================
    def exito(ventana_carga):
        ventana_carga.destroy()
        respuesta = messagebox.askyesno("Proceso Finalizado", "Video cortado con éxito.\n\n¿Desea hacerlo de nuevo con otro video?")
        if respuesta:
            # Reseteamos los valores a su estado inicial
            ruta_archivo.set("Ningún archivo seleccionado")
            ruta_salida.set("Por defecto (carpeta 'partes_nombrevideo')") 
            root.deiconify()
        else:
            root.destroy()

    def error(ventana_carga, msj):
        ventana_carga.destroy()
        messagebox.showerror("Error", f"Ocurrió un problema:\n{msj}")
        root.deiconify()

    # ==========================================
    # DIBUJADO DE LA INTERFAZ PRINCIPAL
    # ==========================================
    tk.Label(root, text="Archivo de Video:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=10)
    tk.Label(root, textvariable=ruta_archivo, fg="blue", wraplength=200, justify="left").grid(row=0, column=1, sticky="w", padx=10)
    tk.Button(root, text="Seleccionar Archivo", command=seleccionar_archivo).grid(row=0, column=2, padx=10)

    tk.Label(root, text="Límite de tamaño (MB):", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=10)
    tk.Entry(root, textvariable=limite_mb, width=10).grid(row=1, column=1, sticky="w", padx=10)

    tk.Label(root, text="Carpeta de salida:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w", pady=10)
    tk.Label(root, textvariable=ruta_salida, fg="gray", wraplength=200, justify="left").grid(row=2, column=1, sticky="w", padx=10)
    tk.Button(root, text="Seleccionar Ruta", command=seleccionar_carpeta).grid(row=2, column=2, padx=10)

    frame_btns = tk.Frame(root)
    frame_btns.grid(row=3, column=0, columnspan=3, pady=20)
    tk.Button(frame_btns, text="Aceptar", command=iniciar_proceso, bg="#4CAF50", fg="white", width=15, font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=10)
    tk.Button(frame_btns, text="Cancelar", command=lambda: root.destroy(), bg="#f44336", fg="white", width=15, font=("Arial", 10, "bold")).pack(side=tk.RIGHT, padx=10)

    root.mainloop()