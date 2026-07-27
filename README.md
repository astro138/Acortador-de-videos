# Acortador de Videos para WhatsApp

Una herramienta gráfica desarrollada en Python para dividir videos automáticamente en partes iguales, asegurando que ninguna partición exceda un límite de tamaño específico (por ejemplo, el límite de 63 MB de WhatsApp).

**Autor:** Alan Lobos Román  
**Versión:** 3.0 - Arquitectura Modular y UI Avanzada  
**Fecha:** Julio 2026  

---

## Características

- **Interfaz Gráfica Intuitiva:** Interfaz construida con Tkinter (amigable y fácil de usar).
- **Auto-cálculo inteligente:** Analiza la duración y el tamaño del video, previniendo procesamientos innecesarios si el video original ya pesa menos que el límite.
- **Rutas Dinámicas:** Si no se especifica una carpeta de guardado, genera automáticamente una carpeta llamada `partes_nombrevideo` en el mismo directorio del video original.
- **Doble Confirmación:** Muestra el número de partes y el tiempo estimado de renderizado antes de comenzar.
- **Progreso Visual Dual:** 
  - Pantalla de carga visual con un cronómetro de segundos por partición en la interfaz.
  - Reporte de consola interactivo con barras de progreso exactas (`logger='bar'`).
- **Threading Integrado:** El proceso corre en segundo plano para evitar que la interfaz visual se congele (not responding) durante videos largos.

## Estructura del Proyecto

El código aplica el patrón de diseño modular separando la interfaz de la lógica:

- `main.py`: Punto de entrada del programa. Conecta la lógica y la interfaz gráfica y gestiona la creación de rutas dinámicas.
- `logica.py`: El "motor" del programa. Se apoya en *MoviePy* para calcular los pesos, analizar los videos, verificar pistas de audio y exportar los archivos `.mp4`.
- `interfaz.py`: Toda la arquitectura visual (ventanas, botones, messagebox, hilos de ejecución secundaria y relojes).

## Requisitos de Instalación

1. Tener instalado [Python 3.7 o superior](https://www.python.org/downloads/).
2. Instalar la librería `moviepy` abriendo tu consola/terminal y ejecutando:
   
   ```bash
   pip install moviepy