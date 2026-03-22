import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
from fpdf import FPDF

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



# --- 4. PANEL DE ADMINISTRACIÓN (SIDEBAR) ---
with st.sidebar:
    st.markdown("### ⚙️ Panel de Administración")
    
    # Campo de contraseña
    clave_ingresada = st.text_input("Clave de acceso:", type="password")
    
    # Verificamos si la clave coincide con la de los Secrets
    if clave_ingresada == st.secrets["general"]["admin_password"]:
        st.success("Acceso concedido")
        st.markdown("---")
        
        # Selector de rango de fechas
        rango_fechas = st.date_input("Seleccionar período a exportar:", [])
        
        # Solo avanzamos si el usuario seleccionó un inicio y un fin
        if len(rango_fechas) == 2:
            fecha_inicio, fecha_fin = rango_fechas
            
            if st.button("Generar PDF de Asistencia", use_container_width=True):
                with st.spinner("Procesando datos..."):
                    # 1. Traer todos los datos de la hoja
                    datos = hoja_asistencia.get_all_records()
                    
                    if not datos:
                        st.warning("No hay registros todavía.")
                    else:
                        # 2. Convertir a DataFrame de Pandas
                        df = pd.DataFrame(datos)
                        
                        # Extraer solo la parte de la fecha (DD/MM/YYYY) para filtrar
                        # Asumiendo que guardaste como "DD/MM/YYYY HH:MM:SS"
                        df['Solo_Fecha'] = pd.to_datetime(df['Fecha y Hora'], format="%d/%m/%Y %H:%M:%S").dt.date
                        
                        # 3. Filtrar por el rango seleccionado
                        mask = (df['Solo_Fecha'] >= fecha_inicio) & (df['Solo_Fecha'] <= fecha_fin)
                        df_filtrado = df.loc[mask].copy()
                        
                        if df_filtrado.empty:
                            st.info("No hay registros para este período.")
                        else:
                            # 4. Mostrar los datos en pantalla para revisión rápida
                            st.write(f"Registros del {fecha_inicio.strftime('%d/%m/%Y')} al {fecha_fin.strftime('%d/%m/%Y')}:")
                            st.dataframe(df_filtrado[['Fecha y Hora', 'Empleado', 'Acción']], hide_index=True)
                            
                            # 5. Generar el PDF
                            pdf = FPDF()
                            pdf.add_page()
                            pdf.set_font("Arial", size=12)
                            
                            # Título del PDF
                            pdf.cell(200, 10, txt=f"Reporte de Asistencia - Estancia San Francisco", ln=True, align='C')
                            pdf.cell(200, 10, txt=f"Periodo: {fecha_inicio.strftime('%d/%m/%Y')} al {fecha_fin.strftime('%d/%m/%Y')}", ln=True, align='C')
                            pdf.ln(10)
                            
                            # Encabezados de tabla en PDF
                            pdf.set_font("Arial", 'B', 10)
                            pdf.cell(60, 10, "Fecha y Hora", border=1)
                            pdf.cell(60, 10, "Empleado", border=1)
                            pdf.cell(40, 10, "Acción", border=1, ln=True)
                            
                            # Filas de datos
                            pdf.set_font("Arial", '', 10)
                            for index, row in df_filtrado.iterrows():
                                pdf.cell(60, 10, str(row['Fecha y Hora']), border=1)
                                pdf.cell(60, 10, str(row['Empleado']), border=1)
                                pdf.cell(40, 10, str(row['Acción']), border=1, ln=True)
                            
                            # Guardar PDF en memoria y crear botón de descarga
                            pdf_output = pdf.output(dest='S').encode('latin-1')
                            
                            st.download_button(
                                label="⬇️ Descargar Reporte en PDF",
                                data=pdf_output,
                                file_name=f"Asistencia_{fecha_inicio}_al_{fecha_fin}.pdf",
                                mime="application/pdf"
                            )
