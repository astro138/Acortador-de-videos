# Acortador de Videos para WhatsApp

Una herramienta gráfica de alto rendimiento desarrollada en Python para dividir videos automáticamente en partes iguales, asegurando que ninguna partición exceda un límite de tamaño específico (por ejemplo, el límite de 63 MB de WhatsApp).

**Autor:** Alan Lobos Román  
**Versión:** 4.0 - Motor FFmpeg de Copia Rápida (Corte Instantáneo)  
**Fecha:** Agosto 2026  

---

## Características

- **Corte Instantáneo sin Pérdida:** Utiliza comandos nativos de FFmpeg (`-c copy`) para realizar copias directas del flujo de video. Lo que antes tardaba minutos en renderizar, ahora toma solo un par de segundos sin perder absolutamente nada de calidad.
- **Reloj Inteligente Dinámico:** Interfaz de carga que muestra el tiempo "Transcurrido" y el tiempo "Restante" en formato clásico `00:00:00`, ajustando dinámicamente el tiempo estimado según el rendimiento de tu PC.
- **Interfaz Gráfica Intuitiva:** Interfaz construida con Tkinter, completamente amigable y fácil de usar.
- **Auto-cálculo de Particiones:** Analiza la duración y el tamaño del video, previniendo procesamientos innecesarios si el video original ya pesa menos que el límite.
- **Rutas Dinámicas:** Si no se especifica una carpeta de guardado, genera automáticamente una carpeta llamada `partes_nombrevideo` en el mismo directorio del video original.
- **Threading Integrado:** El proceso corre en un hilo secundario (background) leyendo la salida de FFmpeg mediante expresiones regulares (Regex). Esto evita que la interfaz visual se congele durante el proceso.

## Estructura del Proyecto

El código aplica un patrón de diseño modular, separando la interfaz de la lógica:

- `main.py`: Punto de entrada del programa. Conecta la lógica y la interfaz gráfica, y gestiona la creación de rutas dinámicas.
- `logica_acortador.py`: El "motor" del programa. Se apoya en *MoviePy* para leer los metadatos iniciales y usa *imageio_ffmpeg* con el módulo *subprocess* para enviar las órdenes de corte ultra rápido.
- `interfaz_acortador.py`: Toda la arquitectura visual (ventanas, botones, messagebox, barras de progreso conectadas a la consola interna y relojes inteligentes).

## Requisitos e Instalación

1. Tener instalado [Python 3.7 o superior](https://www.python.org/downloads/).
2. Instalar las dependencias necesarias abriendo tu consola/terminal y ejecutando:
   
   ```bash
   pip install moviepy imageio-ffmpeg
