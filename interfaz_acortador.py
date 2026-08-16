# By: Alan Lobos Román
# Versión: 4.1 - UI Avanzada (Botones uniformes)
# Fecha: Agosto 2026

import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import threading

def crear_interfaz(comando_analizar, comando_procesar):
    root = tk.Tk()
    root.title("Acortador de Videos Ultra Rápido - Alan Lobos Román")
    root.geometry("550x250")
    root.config(padx=20, pady=20)
    
    ruta_archivo = tk.StringVar(value="Ningún archivo seleccionado")
    ruta_salida = tk.StringVar(value="Por defecto (carpeta 'partes_nombrevideo')")
    limite_mb = tk.StringVar(value="63") 
    
    def seleccionar_archivo():
        ruta = filedialog.askopenfilename(title="Seleccionar Video", filetypes=[("Archivos MP4", "*.mp4")])
        if ruta: ruta_archivo.set(ruta)

    def seleccionar_carpeta():
        ruta = filedialog.askdirectory(title="Seleccionar Carpeta")
        if ruta: ruta_salida.set(ruta)

    def formatear_tiempo(segundos_totales):
        if segundos_totales < 60: return f"Aproximadamente {int(segundos_totales)} seg"
        minutos = int(segundos_totales // 60)
        return f"{minutos} min"

    def formato_reloj(segundos_totales):
        segundos_totales = int(max(0, segundos_totales))
        horas = segundos_totales // 3600
        minutos = (segundos_totales % 3600) // 60
        segundos = segundos_totales % 60
        if horas > 0: return f"{horas:02d}:{minutos:02d}:{segundos:02d}"
        return f"{minutos:02d}:{segundos:02d}"

    def iniciar_proceso():
        archivo = ruta_archivo.get()
        limite = limite_mb.get()
        
        if archivo == "Ningún archivo seleccionado":
            messagebox.showwarning("Atención", "Selecciona un video primero.")
            return
        if not limite.isdigit():
            messagebox.showwarning("Atención", "El límite debe ser numérico.")
            return

        root.withdraw() 
        try:
            partes, tiempo_segundos = comando_analizar(archivo, int(limite))
            if partes == 1:
                messagebox.showinfo("Información", f"El video ya pesa menos del límite.\nNo es necesario cortarlo.")
                root.deiconify() 
                return
            tiempo_texto = formatear_tiempo(tiempo_segundos)
            mostrar_pantalla_confirmacion(archivo, limite, ruta_salida.get(), partes, tiempo_texto, tiempo_segundos)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo leer el video:\n{e}")
            root.deiconify()

    def mostrar_pantalla_confirmacion(archivo, limite, carpeta, partes, tiempo_texto, tiempo_segundos):
        ventana_check = tk.Toplevel(root)
        ventana_check.title("Confirmación")
        # Se ensanchó un poco la ventana para que entren bien los botones grandes
        ventana_check.geometry("430x180")
        ventana_check.config(padx=20, pady=20)
        ventana_check.grab_set() 
        
        mensaje = f"Se dividirá en {partes} partes.\n\nTiempo estimado: {tiempo_texto}.\n\n¿Desea continuar?"
        tk.Label(ventana_check, text=mensaje, font=("Arial", 11), justify="center").pack(pady=10)
        frame_btn = tk.Frame(ventana_check)
        frame_btn.pack(pady=10)
        
        def si_continuar():
            ventana_check.destroy()
            mostrar_pantalla_carga(archivo, limite, carpeta, partes, tiempo_segundos)
            
        def no_continuar():
            ventana_check.destroy()
            root.deiconify() 

        # Botones ahora con exactamente el mismo tamaño y estilo que los de la pantalla principal
        tk.Button(frame_btn, text="Sí, continuar", command=si_continuar, bg="#4CAF50", fg="white", width=15, font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_btn, text="Cancelar", command=no_continuar, bg="#f44336", fg="white", width=15, font=("Arial", 10, "bold")).pack(side=tk.RIGHT, padx=10)

    def mostrar_pantalla_carga(archivo, limite, carpeta, partes_totales, estimado_inicial):
        ventana_carga = tk.Toplevel(root)
        ventana_carga.title("Procesando Rápido...")
        ventana_carga.geometry("380x220") 
        ventana_carga.config(padx=20, pady=20)
        ventana_carga.protocol("WM_DELETE_WINDOW", lambda: None) 
        
        lbl_texto = tk.Label(ventana_carga, text="Preparando copia directa...", font=("Arial", 11, "bold"))
        lbl_texto.pack(pady=5)
        lbl_tiempo = tk.Label(ventana_carga, text="Calculando tiempo restante...", font=("Consolas", 10))
        lbl_tiempo.pack(pady=2)
        lbl_progreso = tk.Label(ventana_carga, text="Iniciando...", font=("Arial", 9, "italic"), fg="blue")
        lbl_progreso.pack(pady=2)
        
        barra = ttk.Progressbar(ventana_carga, orient="horizontal", mode='determinate', length=300)
        barra.pack(fill=tk.X, pady=10)

        estado = {
            "transcurrido": 0,
            "parte_actual": 1,
            "porcentaje_fase": 0,
            "corriendo": True
        }

        def actualizar_reloj():
            if estado["corriendo"]:
                estado["transcurrido"] += 1
                progreso_global = ((estado["parte_actual"] - 1) * 100 + estado["porcentaje_fase"]) / partes_totales

                if progreso_global > 1: 
                    tiempo_total_estimado = (estado["transcurrido"] / progreso_global) * 100
                    restante = tiempo_total_estimado - estado["transcurrido"]
                else:
                    restante = estimado_inicial - estado["transcurrido"]

                txt = f"Transcurrido: {formato_reloj(estado['transcurrido'])} | Restante: {formato_reloj(restante)}"
                lbl_tiempo.config(text=txt)
                ventana_carga.after(1000, actualizar_reloj) 

        def actualizar_texto(parte_actual, total_partes):
            lbl_texto.config(text=f"Cortando partición {parte_actual} de {total_partes}...")
            estado["parte_actual"] = parte_actual
            estado["porcentaje_fase"] = 0
            barra['value'] = 0

        def actualizar_barra(fase, porcentaje):
            def ui_update():
                lbl_progreso.config(text=f"{fase}... {int(porcentaje)}%")
                barra['value'] = porcentaje
                estado["porcentaje_fase"] = porcentaje
            ventana_carga.after(0, ui_update)

        actualizar_reloj() 

        def tarea_fondo():
            try:
                comando_procesar(
                    archivo, int(limite), carpeta, 
                    lambda p, t: root.after(0, actualizar_texto, p, t),
                    actualizar_barra
                )
                estado["corriendo"] = False 
                root.after(0, lambda: exito(ventana_carga))
            except Exception as e:
                estado["corriendo"] = False 
                root.after(0, lambda err=str(e): error(ventana_carga, err))

        threading.Thread(target=tarea_fondo, daemon=True).start()

    def exito(ventana_carga):
        ventana_carga.destroy()
        respuesta = messagebox.askyesno("¡Completado!", "El video fue cortado en tiempo récord.\n\n¿Desea cortar otro video?")
        if respuesta:
            ruta_archivo.set("Ningún archivo seleccionado")
            ruta_salida.set("Por defecto (carpeta 'partes_nombrevideo')") 
            root.deiconify()
        else:
            root.destroy()

    def error(ventana_carga, msj):
        ventana_carga.destroy()
        messagebox.showerror("Error", f"Ocurrió un problema:\n{msj}")
        root.deiconify()

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
