# By: Alan Lobos Román
# Versión: 4.1 - Motor FFmpeg (Copia Directa) + Anti-VBR
# Fecha: Agosto 2026

import os
import re
import math
import subprocess
import threading
import imageio_ffmpeg
from moviepy import VideoFileClip

def asegurarse_directorio(ruta):
    if not os.path.exists(ruta):
        os.makedirs(ruta)

def segundos_a_texto(segundos: float) -> str:
    segundos = int(round(segundos))
    if segundos <= 0: return "0 seg"
    horas = segundos // 3600
    minutos = (segundos % 3600) // 60
    segs = segundos % 60
    partes = []
    if horas > 0: partes.append(f"{horas}h")
    if minutos > 0: partes.append(f"{minutos}m")
    if segs > 0 or not partes: partes.append(f"{segs}s")
    return " ".join(partes)

def calcular_partes_seguras(tamaño_total, limite_mb):
    """
    Usa un margen de seguridad del 35% (0.65) para evitar que
    los picos de Bitrate Variable (VBR) excedan el límite ingresado.
    """
    margen_vbr = 0.65 
    limite_seguro = limite_mb * margen_vbr
    partes = math.ceil(tamaño_total / limite_seguro)
    return max(1, partes)

def analizar_video(video_path, limite_mb):
    clip = VideoFileClip(video_path)
    tamaño_total = os.path.getsize(video_path) / (1024 * 1024)
    clip.close()

    # Ahora usa el cálculo con margen de seguridad
    partes = calcular_partes_seguras(tamaño_total, limite_mb)
    tiempo_estimado_segundos = partes * 2.0 
    
    return partes, tiempo_estimado_segundos

def dividir_video_por_tamaño(video_path, salida_dir, limite_mb, callback_nueva_parte=None, callback_progreso=None):
    clip = VideoFileClip(video_path)
    duracion_total = clip.duration
    tamaño_total = os.path.getsize(video_path) / (1024 * 1024)
    clip.close()

    # Ahora usa el cálculo con margen de seguridad
    partes = calcular_partes_seguras(tamaño_total, limite_mb)
    duracion_por_parte = duracion_total / partes
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    regex_tiempo = re.compile(r"time=(\d+):(\d+):(\d+\.\d+)")

    for i in range(partes):
        if callback_nueva_parte:
            callback_nueva_parte(i + 1, partes)

        inicio = i * duracion_por_parte
        salida_path = os.path.join(salida_dir, f"parte_{i+1}.mp4")

        comando = [
            ffmpeg_exe, "-y", 
            "-ss", str(inicio), 
            "-i", video_path, 
            "-t", str(duracion_por_parte), 
            "-c", "copy", 
            salida_path
        ]

        proceso = subprocess.Popen(
            comando, 
            stderr=subprocess.PIPE, 
            universal_newlines=True, 
            encoding='utf-8', 
            errors='ignore'
        )

        for linea in proceso.stderr:
            match = regex_tiempo.search(linea)
            if match and callback_progreso:
                h, m, s = match.groups()
                tiempo_actual = int(h)*3600 + int(m)*60 + float(s)
                porcentaje = (tiempo_actual / duracion_por_parte) * 100
                if porcentaje > 100: porcentaje = 100
                callback_progreso("Copia Rápida", porcentaje)

        proceso.wait()
        
        if callback_progreso:
            callback_progreso("Finalizando parte", 100.0)
