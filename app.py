import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from zoneinfo import ZoneInfo

# --- 1. CONFIGURACIÓN DE PÁGINA Y CSS ---
st.set_page_config(page_title="Asistencia - Estancia San Francisco", layout="centered")

st.markdown("""
    <style>
    /* Estilo base botones */
    div.stButton > button {
        height: 120px;          
        font-size: 30px;        
        font-weight: bold;      
        border-radius: 20px;    
        width: 100%;            
        transition: all 0.2s;   
        border: none;           
    }
    div.stButton > button:hover { transform: scale(1.03); }

    /* BOTÓN 1 (ENTRADA) - Verde */
    div[data-testid="column"]:nth-of-type(1) div.stButton > button {
        background-color: #2e7d32; 
        color: white;             
        box-shadow: 0 4px 15px rgba(46, 125, 50, 0.4); 
    }
    div[data-testid="column"]:nth-of-type(1) div.stButton > button:hover { background-color: #1b5e20; }

    /* BOTÓN 2 (SALIDA) - Amarillo */
    div[data-testid="column"]:nth-of-type(2) div.stButton > button {
        background-color: #ffca28; 
        color: #333333;           
        box-shadow: 0 4px 15px rgba(255, 202, 40, 0.4); 
    }
    div[data-testid="column"]:nth-of-type(2) div.stButton > button:hover { background-color: #ffb300; }

    /* Texto Selectbox */
    div[data-baseweb="select"] > div { font-size: 18px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. CONEXIÓN A GOOGLE SHEETS ---
@st.cache_resource
def conectar_sheets():
    # Definir permisos
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # Tomar credenciales leyendo la ruta exacta de tu st.secrets
    credenciales_dict = dict(st.secrets["connections"]["gsheets"])
    
    # Autorizar conexión con la librería moderna
    creds = Credentials.from_service_account_info(credenciales_dict, scopes=scopes)
    cliente = gspread.authorize(creds)
    
    # Abrimos el archivo usando tu ID único de Google Sheets
    id_planilla = "1fyiKYB0_3HV4qI58rMVBL8TVsgX8Cs5i1RoghAWlHoY"
    archivo_sheets = cliente.open_by_key(id_planilla)
    
    # Apuntamos a la pestaña "Asistencia"
    hoja = archivo_sheets.worksheet("Asistencia")
    return hoja

# Intentar conectar
try:
    hoja_asistencia = conectar_sheets()
except Exception as e:
    st.error(f"Error al conectar con Google Sheets: {e}")
    st.stop()

# --- 3. INTERFAZ Y LÓGICA ---
st.title("Registro de Personal")
st.markdown("Seleccioná tu nombre y registrá tu horario.")

# Nombres de tu equipo
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

nombre = st.selectbox("Empleado:", empleados)

if nombre != "Seleccionar...":
    st.write("---") 
    col1, col2 = st.columns(2)
    zona_ar = ZoneInfo("America/Argentina/Buenos_Aires")
    
    with col1:
        if st.button("ENTRADA", use_container_width=True):
            hora_actual = datetime.now(zona_ar).strftime("%d/%m/%Y %H:%M:%S")
            # Enviar a Google Sheets
            hoja_asistencia.append_row([hora_actual, nombre, "ENTRADA"])
            st.success(f"Entrada registrada.\n\n**{nombre}** - {hora_actual}")
            
    with col2:
        if st.button("SALIDA", use_container_width=True):
            hora_actual = datetime.now(zona_ar).strftime("%d/%m/%Y %H:%M:%S")
            # Enviar a Google Sheets
            hoja_asistencia.append_row([hora_actual, nombre, "SALIDA"])
            st.warning(f"Salida registrada.\n\n**{nombre}** - {hora_actual}")
