# By: Alan Lobos Román
# Versión: 3.0 - Arquitectura Modular y UI Avanzada
# Fecha: Julio 2026
# Descripción: 
# Módulo lógico. Se encarga de analizar y cortar el video usando
# MoviePy. Realiza los cálculos de tiempo/peso y muestra el
# progreso detallado en la consola.

import os
from moviepy import VideoFileClip


def asegurarse_directorio(ruta):
    """Verifica si un directorio existe, y si no, lo crea."""
    if not os.path.exists(ruta):
        os.makedirs(ruta)

def segundos_a_texto(segundos: float) -> str:
    """Convierte una cantidad de segundos a un formato de texto legible."""
    segundos = int(round(segundos))
    if segundos <= 0:
        return "0 seg"

    horas = segundos // 3600
    minutos = (segundos % 3600) // 60
    segs = segundos % 60

    partes = []
    if horas > 0:
        partes.append(f"{horas} hora" if horas == 1 else f"{horas} horas")
    if minutos > 0:
        partes.append(f"{minutos} min")
    if segs > 0 or not partes:
        partes.append(f"{segs} seg")

    if len(partes) == 1:
        return partes[0]
    elif len(partes) == 2:
        return f"{partes[0]} y {partes[1]}"
    else:
        return f"{partes[0]}, {partes[1]} con {partes[2]}"

def analizar_video(video_path, limite_mb):
    """
    Abre el video brevemente para leer su duración y peso total.
    Retorna la cantidad de partes en las que se dividirá y un tiempo estimado.
    """
    clip = VideoFileClip(video_path)
    duracion_total = clip.duration
    tamaño_total = os.path.getsize(video_path) / (1024 * 1024)
    clip.close()

    partes = int(tamaño_total // limite_mb) + 1
    tiempo_estimado_segundos = duracion_total * 0.4 
    
    return partes, tiempo_estimado_segundos

def dividir_video_por_tamaño(video_path, salida_dir, limite_mb, callback_nueva_parte=None):
    """
    Procesa y corta el video en partes iguales basándose en el límite de MB.
    Genera reportes por consola y avisa a la interfaz cuando inicia una nueva parte.
    """
    clip = VideoFileClip(video_path)
    duracion_total = clip.duration
    tamaño_total = os.path.getsize(video_path) / (1024 * 1024)

    partes = int(tamaño_total // limite_mb) + 1
    duracion_por_parte = duracion_total / partes

    # Verificación de audio para evitar cuelgues si el video es mudo
    tiene_audio = clip.audio is not None

    print("\n" + "=" * 55)
    print(f" Archivo:        {os.path.basename(video_path)}")
    print(f" Duración total: {segundos_a_texto(duracion_total)}")
    print(f" Tamaño total:   {tamaño_total:.2f} MB")
    print(f" Límite p/parte: {limite_mb} MB")
    print(f" Partes:         {partes} (de ~{segundos_a_texto(duracion_por_parte)} c/u)")
    print(f" Guardando en:   {salida_dir}")
    print("=" * 55 + "\n")

    for i in range(partes):
        # Avisamos a la interfaz que empezamos una nueva partición (para el cronómetro visual)
        if callback_nueva_parte:
            callback_nueva_parte(i + 1, partes)

        inicio = i * duracion_por_parte
        fin = min((i + 1) * duracion_por_parte, duracion_total)

        subclip = clip.subclipped(inicio, fin)
        salida_path = os.path.join(salida_dir, f"parte_{i+1}.mp4")
        temp_audio = os.path.join(salida_dir, f'temp_audio_{i+1}.m4a')

        print(f"\n[Parte {i+1}/{partes}] Cortando tramo: {segundos_a_texto(inicio)} ➔ {segundos_a_texto(fin)}")

        subclip.write_videofile(
            salida_path,
            codec="libx264",
            audio=tiene_audio,
            audio_codec="aac" if tiene_audio else None,
            temp_audiofile=temp_audio if tiene_audio else None,
            remove_temp=True,
            logger='bar'  # <-- AQUÍ ESTÁ LA PANTALLA DE CARGA EN CONSOLA QUE PEDISTE
        )
        
        subclip.close()

    clip.close()
    print("\n ¡Proceso completado exitosamente!")