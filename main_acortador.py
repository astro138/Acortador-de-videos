# By: Alan Lobos Román
# Versión: 3.0 - Arquitectura Modular y UI Avanzada
# Fecha: Julio 2026
# Descripción: 
# Módulo de Interfaz Gráfica (GUI) usando Tkinter. Maneja el 
# flujo visual: Selección, Confirmación, Pantalla de Carga 
#con cronómetro y procesamiento en segundo plano (Threading).

import os
from logica_acortador import asegurarse_directorio, dividir_video_por_tamaño, analizar_video
from interfaz_acortador import crear_interfaz

def funcion_analizar(archivo, limite):
    return analizar_video(archivo, limite)

def funcion_procesar(archivo, limite, carpeta, callback_nueva_parte):
    # Verificamos si es la opción por defecto de la interfaz
    if carpeta == "Por defecto (carpeta 'partes_nombrevideo')":
        directorio_video = os.path.dirname(archivo)
        # Extraemos el nombre del video sin la extensión (.mp4) 
        nombre_video_sin_ext = os.path.splitext(os.path.basename(archivo))[0]
        # Creamos el nombre de la carpeta: partes_nombrevideo
        nombre_carpeta = f"partes_{nombre_video_sin_ext}"
        carpeta_final = os.path.join(directorio_video, nombre_carpeta)
    else:
        carpeta_final = carpeta

    asegurarse_directorio(carpeta_final)
    
    dividir_video_por_tamaño(archivo, carpeta_final, limite, callback_nueva_parte)

if __name__ == '__main__':
    crear_interfaz(funcion_analizar, funcion_procesar)