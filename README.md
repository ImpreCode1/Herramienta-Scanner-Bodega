# 🗂️ Herramienta de Scanner en Bodega

**Descripción**

La Herramienta de Scanner es un proyecto en Python para automatizar el procesamiento de documentos escaneados en formato PDF, específicamente facturas. El sistema detecta códigos de barras en cada página de un PDF, agrupa las páginas que pertenecen a una misma factura y genera un PDF separado por cada factura encontrada. Este proyecto tiene como objetivo agilizar el proceso de escaneo y clasificación de facturas en la empresa, eliminando la necesidad de organización manual de documentos.


## Características principales  
- Detección automática de códigos de barras en cada página del documento.
- Agrupación de páginas por factura según el código de barras.
- Generación de PDFs individuales para cada factura detectada.
- Generación de un reporte con detalles del proceso (número de facturas, páginas sin código, errores detectados, etc.).
- Funciona sin conexión a Internet, ideal para entornos corporativos.
- Fácil de usar: interfaz simple de línea de comandos o interfaz gráfica básica.

### Tecnologías usadas  
- Python 3.10+

- PyMuPDF (fitz): para procesar PDFs.

- pyzbar: para la detección de códigos de barras.

- pdf2image: para convertir páginas de PDF a imágenes.

- OpenCV (opcional): para mejorar la precisión de la detección de códigos de barras.

- PyInstaller: para generar un ejecutable .exe en Windows.

- PyQt5 (opcional): para interfaz gráfica básica.

### Requisitos
Para ejecutar este proyecto en tu máquina, asegúrate de tener instalado Python 3.10+ y las siguientes librerías:
```bash
pip install -r requirements.txt
```
