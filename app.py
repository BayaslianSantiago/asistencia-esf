import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo

# 1. Configuración de la página
st.set_page_config(
    page_title="Asistencia - Estancia San Francisco", 
    layout="centered"
)

# ------------------------------------------------------------------
# CSS PARA BOTONES COLOREADOS Y GIGANTES
# ------------------------------------------------------------------
st.markdown("""
    <style>
    /* Estilo BASE común para ambos botones gigantes */
    div.stButton > button {
        height: 120px;          
        font-size: 30px;        
        font-weight: bold;      
        border-radius: 20px;    
        width: 100%;            
        transition: all 0.2s;   
        border: none;           
    }
    
    div.stButton > button:hover {
        transform: scale(1.03); 
    }

    /* --- ESTILO ESPECÍFICO PARA EL BOTÓN 1 (ENTRADA) --- */
    div[data-testid="column"]:nth-of-type(1) div.stButton > button {
        background-color: #2e7d32; /* Verde esmeralda oscuro */
        color: white;             
        box-shadow: 0 4px 15px rgba(46, 125, 50, 0.4); 
    }
    div[data-testid="column"]:nth-of-type(1) div.stButton > button:hover {
        background-color: #1b5e20; 
    }

    /* --- ESTILO ESPECÍFICO PARA EL BOTÓN 2 (SALIDA) --- */
    div[data-testid="column"]:nth-of-type(2) div.stButton > button {
        background-color: #ffca28; /* Amarillo / Ámbar agradable */
        color: #333333;           /* Texto oscuro para buen contraste */
        box-shadow: 0 4px 15px rgba(255, 202, 40, 0.4); 
    }
    div[data-testid="column"]:nth-of-type(2) div.stButton > button:hover {
        background-color: #ffb300; /* Amarillo más oscuro al pasar el mouse */
    }

    /* Estilo para el texto 'Empleado:' del selectbox */
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
            st.success(f"Entrada registrada.\n\n**{nombre}** - {hora_actual}")
            
            # TODO: Conectar a Google Sheets
            
    with col2:
        # Botón de SALIDA
        if st.button("SALIDA", use_container_width=True):
            hora_actual = datetime.now(zona_ar).strftime("%d/%m/%Y %H:%M:%S")
            # Volvemos a st.warning para que coincida con el amarillo
            st.warning(f"Salida registrada.\n\n**{nombre}** - {hora_actual}")
            
            # TODO: Conectar a Google Sheets
