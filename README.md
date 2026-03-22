# ⏱️ Sistema de Control de Asistencia

Una aplicación web ligera y optimizada para dispositivos móviles, construida con **Python** y **Streamlit**. Diseñada para gestionar el registro de entrada y salida del personal en entornos comerciales, sincronizando los datos en tiempo real con **Google Sheets** y generando reportes automatizados en PDF.

Desarrollada para cumplir con normativas de control horario e integrarse fluidamente en el día a día operativo de una cadena de fiambrerías.

## ✨ Características Principales

* **Interfaz Mobile-First:** UI minimalista con botones táctiles de gran tamaño y código de colores (Verde/Amarillo) para un fichaje rápido y sin fricciones.
* **Base de Datos Serverless:** Integración directa con la API de Google Sheets a través de credenciales de Google Cloud (GCP) como Service Account.
* **Validación de Datos en Tiempo Real:** Lógica implementada con `pandas` para evitar fichajes dobles (ej. registrar dos entradas el mismo día por error humano).
* **Panel de Administración Seguro:** Área restringida mediante contraseña (gestionada vía variables de entorno) para la administración del sistema.
* **Generación de Reportes PDF:** Motor de exportación que utiliza Tablas Dinámicas (Pivot Tables) de `pandas` para estructurar los datos brutos en un formato legible (Fecha | Empleado | Entrada | Salida) y los compila en un PDF listo para imprimir usando `fpdf`.

## 🛠️ Stack Tecnológico

* **Frontend & Framework:** [Streamlit](https://streamlit.io/)
* **Procesamiento de Datos:** [Pandas](https://pandas.pydata.org/)
* **Conexión a Base de Datos:** `gspread`, `google-auth` (Google Cloud IAM)
* **Generación de Documentos:** `fpdf`
* **Manejo de Tiempos:** `datetime`, `zoneinfo` (Zona horaria forzada a Buenos Aires)

## 🚀 Instalación y Despliegue Local

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/tu-usuario/tu-repositorio.git](https://github.com/tu-usuario/tu-repositorio.git)
   cd tu-repositorio
