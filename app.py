import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo # Ideal para manejar la zona horaria sin instalar librerías extra

# 1. Configuración de la página (optimizada para celular)
st.set_page_config(
    page_title="Asistencia - Estancia San Francisco", 
    page_icon="⏱️", 
    layout="centered"
)

st.title("⏱️ Registro de Personal")
st.markdown("Seleccioná tu nombre y registrá tu horario.")

# 2. Lista de empleados (reemplazar con los nombres reales de los 7)
empleados = [
    "Seleccionar...", 
    "Santiago", 
    "Julieta", 
    "Mariel", 
    "Fernanda", 
    "Brian", 
    "Eika", 
    "Oriana"
]

# 3. El selector de nombres
nombre = st.selectbox("👤 Empleado:", empleados)

# 4. Lógica de la interfaz: Los botones solo aparecen si se eligió un nombre
if nombre != "Seleccionar...":
    st.write("---") # Una línea separadora para que quede prolijo
    
    # Creamos dos columnas de igual tamaño
    col1, col2 = st.columns(2)
    
    # Zona horaria de Argentina
    zona_ar = ZoneInfo("America/Argentina/Buenos_Aires")
    
    with col1:
        # Botón de ENTRADA
        if st.button("🟢 ENTRADA", use_container_width=True):
            hora_actual = datetime.now(zona_ar).strftime("%Y-%m-%d %H:%M:%S")
            # Mensaje de éxito temporal
            st.success(f"✅ Entrada registrada con éxito.\n\n**{nombre}** - {hora_actual}")
            
            # TODO: Aquí irá el código para enviar los datos a Google Sheets
            
    with col2:
        # Botón de SALIDA
        if st.button("🔴 SALIDA", use_container_width=True):
            hora_actual = datetime.now(zona_ar).strftime("%Y-%m-%d %H:%M:%S")
            # Mensaje de aviso temporal
            st.warning(f"👋 Salida registrada con éxito.\n\n**{nombre}** - {hora_actual}")
            
            # TODO: Aquí irá el código para enviar los datos a Google Sheets
