# CeNET - Gestor de certificados y actas

Aplicación de escritorio en Python (Tkinter) para descargar certificados desde Moodle y exportar actas académicas en estructuras normalizadas. El proyecto está preparado para empaquetarse como un ejecutable único con PyInstaller.

## Requisitos

- Python 3.10 o superior.
- Dependencias listadas en `requirements.txt`.

Instale los paquetes necesarios:

```bash
python -m venv .venv
source .venv/bin/activate  # En Windows use .venv\\Scripts\\activate
pip install -r requirements.txt
```

## Ejecución

```bash
python -m app.main
```

Al iniciar verá la pantalla principal con dos flujos:

- **Descargar certificados:** requiere CSV base, credenciales de Moodle, carpeta de salida y links o CSV de mapeo. Genera zips agrupados por provincia y logs de auditoría.
- **Exportar actas:** acepta múltiples CSV/PDF, produce PDFs normalizados, zips por provincia y resumen de exportación.

La aplicación guarda la configuración básica en `config.ini` (URL de Moodle, modalidad, cohorte, año y última carpeta de salida) para autocompletar formularios futuros.

## Estructura de salidas

- `jurisdicciones/<Provincia>/<Modalidad>_<Año>_<Cohorte>.zip`
  - Contiene subcarpetas por curso con certificados o PDFs de aprobados según el flujo ejecutado.
- `actas/<Modalidad>_<Año>_<Cohorte>.zip`
  - Incluye las actas (CSV convertidos a PDF o PDFs originales) organizadas por curso/comisión.
- `log_descargas.csv`, `log_parseo.txt`, `resumen_exportacion.csv`, según corresponda.
- `app.log` registra todos los eventos.

## Datos de ejemplo

En la carpeta `examples/` encontrará archivos listos para pruebas manuales:

- `certificados_base.csv` y `certificados_links.csv`
- `acta_ejemplo.csv` y `acta_ejemplo.pdf`

## Validaciones automáticas de estructura

Tras ejecutar un flujo puede validar la estructura generada:

```bash
python -m app.tests.validators certificados <ruta_salida>
python -m app.tests.validators actas <ruta_salida>
```

Los comandos devuelven un resumen JSON indicando si se detectaron los componentes esperados.

## Empaquetado con PyInstaller

1. Instale PyInstaller si aún no lo tiene: `pip install pyinstaller`.
2. Ejecute:

   ```bash
   pyinstaller CeNET.spec --clean
   ```

El ejecutable se generará en `dist/CeNET/`. El spec ya incluye los datos y la configuración necesaria para un único binario.

## Notas técnicas

- Los procesos intensivos se ejecutan en hilos para mantener la GUI responsive.
- Se implementa reintento exponencial para descargas HTTP y validaciones inline en formularios.
- Se generan PDFs con ReportLab y se analizan PDFs con pdfplumber.
- Las rutas y nombres se normalizan para evitar caracteres inválidos.

