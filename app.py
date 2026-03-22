import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo

# 1. Configuración de la página
st.set_page_config(
    page_title="Asistencia - Estancia San Francisco", 
    layout="centered"
)

# ------------------------------------------------------------------
# TRUCO DE CSS PARA BOTONES GIGANTES
# Esto afecta a todos los botones 'st.button' de la aplicación
# ------------------------------------------------------------------
st.markdown("""
    <style>
    /* Estilo general para los botones st.button */
    div.stButton > button {
        height: 120px;          /* Altura del botón (enorme) */
        font-size: 30px;        /* Tamaño de la letra */
        font-weight: bold;      /* Letra negrita */
        border-radius: 15px;    /* Bordes redondeados */
        width: 100%;            /* Ocupar todo el ancho de la columna */
        transition: all 0.3s;   /* Animación suave al pasar el mouse */
    }
    
    /* Efecto al pasar el mouse (para desktop) */
    div.stButton > button:hover {
        opacity: 0.8;
        transform: scale(1.02); /* Se agranda un poquito */
    }
    
    /* Estilo específico para el texto 'Empleado:' del selectbox */
    div[data-baseweb="select"] > div {
        font-size: 18px;
    }
    </style>
""", unsafe_allow_html=True)
# ------------------------------------------------------------------

st.title("Registro de Personal")
st.markdown("Seleccioná tu nombre y registrá tu horario.")

# 2. Lista de empleados
empleados = [
    "Seleccionar...", 
    "Santiago", 
    "Compañero 2", 
    "Compañero 3", 
    "Compañero 4", 
    "Compañero 5", 
    "Compañero 6", 
    "Compañero 7"
]

# 3. El selector de nombres
nombre = st.selectbox("Empleado:", empleados)

# 4. Lógica de la interfaz
if nombre != "Seleccionar...":
    st.write("---") 
    
    col1, col2 = st.columns(2)
    
    zona_ar = ZoneInfo("America/Argentina/Buenos_Aires")
    
    with col1:
        # Botón de ENTRADA
        if st.button("ENTRADA", use_container_width=True):
            hora_actual = datetime.now(zona_ar).strftime("%d/%m/%Y %H:%M:%S")
            # Feedback visual (los mensajes st.success también se pueden customizar con CSS si hiciera falta)
            st.success(f"Entrada registrada.\n\n**{nombre}** - {hora_actual}")
            
            # TODO: Conectar a Google Sheets
            
    with col2:
        # Botón de SALIDA
        if st.button("SALIDA", use_container_width=True):
            hora_actual = datetime.now(zona_ar).strftime("%d/%m/%Y %H:%M:%S")
            st.warning(f"Salida registrada.\n\n**{nombre}** - {hora_actual}")
            
            # TODO: Conectar a Google Sheets
