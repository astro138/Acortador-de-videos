import os
from logica_acortador import asegurarse_directorio, dividir_video_por_tamaño, analizar_video
from interfaz_acortador import crear_interfaz

def funcion_analizar(archivo, limite):
    return analizar_video(archivo, limite)

def funcion_procesar(archivo, limite, carpeta, callback_nueva_parte, callback_progreso):
    if carpeta == "Por defecto (carpeta 'partes_nombrevideo')":
        directorio_video = os.path.dirname(archivo)
        nombre_video_sin_ext = os.path.splitext(os.path.basename(archivo))[0]
        nombre_carpeta = f"partes_{nombre_video_sin_ext}"
        carpeta_final = os.path.join(directorio_video, nombre_carpeta)
    else:
        carpeta_final = carpeta

    asegurarse_directorio(carpeta_final)
    
    dividir_video_por_tamaño(archivo, carpeta_final, limite, callback_nueva_parte, callback_progreso)

if __name__ == '__main__':
    crear_interfaz(funcion_analizar, funcion_procesar)
