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

    /* BOTÓN 1 (ENTRADA) */
    div[data-testid="column"]:nth-of-type(1) div.stButton > button {
        background-color: #2e7d32; 
        color: white;             
        box-shadow: 0 4px 15px rgba(46, 125, 50, 0.4); 
    }
    div[data-testid="column"]:nth-of-type(1) div.stButton > button:hover { background-color: #1b5e20; }

    /* BOTÓN 2 (SALIDA) */
    div[data-testid="column"]:nth-of-type(2) div.stButton > button {
        background-color: #ffca28; 
        color: #333333;           
        box-shadow: 0 4px 15px rgba(255, 202, 40, 0.4); 
    }
    div[data-testid="column"]:nth-of-type(2) div.stButton > button:hover { background-color: #ffb300; }

    div[data-baseweb="select"] > div { font-size: 18px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. CONEXIÓN A GOOGLE SHEETS ---
@st.cache_resource
def conectar_sheets():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    credenciales_dict = dict(st.secrets["connections"]["gsheets"])
    creds = Credentials.from_service_account_info(credenciales_dict, scopes=scopes)
    cliente = gspread.authorize(creds)
    id_planilla = "1fyiKYB0_3HV4qI58rMVBL8TVsgX8Cs5i1RoghAWlHoY"
    archivo_sheets = cliente.open_by_key(id_planilla)
    hoja = archivo_sheets.worksheet("Asistencia")
    return hoja

try:
    hoja_asistencia = conectar_sheets()
except Exception as e:
    st.error(f"Error al conectar con Google Sheets: {e}")
    st.stop()

# --- 3. INTERFAZ Y LÓGICA DE FICHADA ---
st.title("Registro de Personal")
st.markdown("Seleccioná tu nombre y registrá tu horario.")

empleados = [
    "Seleccionar...", 
    "Brian", Brian Erika Fernanda Julieta Mariel Oriana Santiago
    "Erika", 
    "Fernanda", 
    "Juliera", 
    "Mariel", 
    "Oriana", 
    "Santiago"
]

nombre = st.selectbox("Empleado:", empleados)

if nombre != "Seleccionar...":
    st.write("---") 
    col1, col2 = st.columns(2)
    zona_ar = ZoneInfo("America/Argentina/Buenos_Aires")
    
    with col1:
        if st.button("ENTRADA", use_container_width=True):
            ahora = datetime.now(zona_ar)
            fecha_hoy = ahora.strftime("%d/%m/%Y")
            hora_actual = ahora.strftime("%d/%m/%Y %H:%M:%S")
            
            # Validación de fichaje doble
            datos = hoja_asistencia.get_all_records()
            ya_ficho = False
            if datos:
                df = pd.DataFrame(datos)
                # Filtramos si existe registro de hoy, de esta persona, que sea ENTRADA
                filtro = (df['Fecha y Hora'].str.startswith(fecha_hoy)) & (df['Empleado'] == nombre) & (df['Acción'] == 'ENTRADA')
                if not df[filtro].empty:
                    ya_ficho = True
            
            if ya_ficho:
                st.error(f"⚠️ {nombre}, ya registraste tu ENTRADA el día de hoy.")
            else:
                hoja_asistencia.append_row([hora_actual, nombre, "ENTRADA"])
                st.success(f"Entrada registrada.\n\n**{nombre}** - {hora_actual}")
            
    with col2:
        if st.button("SALIDA", use_container_width=True):
            ahora = datetime.now(zona_ar)
            fecha_hoy = ahora.strftime("%d/%m/%Y")
            hora_actual = ahora.strftime("%d/%m/%Y %H:%M:%S")
            
            # Validación de fichaje doble
            datos = hoja_asistencia.get_all_records()
            ya_ficho = False
            if datos:
                df = pd.DataFrame(datos)
                # Filtramos si existe registro de hoy, de esta persona, que sea SALIDA
                filtro = (df['Fecha y Hora'].str.startswith(fecha_hoy)) & (df['Empleado'] == nombre) & (df['Acción'] == 'SALIDA')
                if not df[filtro].empty:
                    ya_ficho = True
                    
            if ya_ficho:
                st.error(f"⚠️ {nombre}, ya registraste tu SALIDA el día de hoy.")
            else:
                hoja_asistencia.append_row([hora_actual, nombre, "SALIDA"])
                st.warning(f"Salida registrada.\n\n**{nombre}** - {hora_actual}")


# --- 4. PANEL DE ADMINISTRACIÓN (SIDEBAR) ---
with st.sidebar:
    st.markdown("### ⚙️ Panel de Administración")
    
    clave_ingresada = st.text_input("Clave de acceso:", type="password")
    
    if clave_ingresada == st.secrets["general"]["admin_password"]:
        st.success("Acceso concedido")
        st.markdown("---")
        
        rango_fechas = st.date_input("Seleccionar período a exportar:", [])
        
        if len(rango_fechas) == 2:
            fecha_inicio, fecha_fin = rango_fechas
            
            if st.button("Generar PDF de Asistencia", use_container_width=True):
                with st.spinner("Procesando datos..."):
                    datos = hoja_asistencia.get_all_records()
                    
                    if not datos:
                        st.warning("No hay registros todavía.")
                    else:
                        df = pd.DataFrame(datos)
                        
                        # 1. Transformación de datos (Data Science en acción)
                        # Convertimos el string a objeto datetime para poder filtrar y separar
                        df['Datetime'] = pd.to_datetime(df['Fecha y Hora'], format="%d/%m/%Y %H:%M:%S")
                        df['Fecha_str'] = df['Datetime'].dt.strftime('%d/%m/%Y')
                        df['Hora_str'] = df['Datetime'].dt.strftime('%H:%M:%S')
                        df['Solo_Fecha'] = df['Datetime'].dt.date
                        
                        # 2. Filtramos por el rango seleccionado
                        mask = (df['Solo_Fecha'] >= fecha_inicio) & (df['Solo_Fecha'] <= fecha_fin)
                        df_filtrado = df.loc[mask].copy()
                        
                        if df_filtrado.empty:
                            st.info("No hay registros para este período.")
                        else:
                            # 3. Pivot Table: agrupamos todo en una sola fila por persona y día
                            df_pivot = df_filtrado.pivot_table(
                                index=['Fecha_str', 'Empleado'], 
                                columns='Acción', 
                                values='Hora_str', 
                                aggfunc='first'
                            ).reset_index()
                            
                            # Aseguramos que existan las columnas, por si nadie fichó entrada o salida
                            if 'ENTRADA' not in df_pivot.columns: df_pivot['ENTRADA'] = '-'
                            if 'SALIDA' not in df_pivot.columns: df_pivot['SALIDA'] = '-'
                            
                            # Llenamos los espacios vacíos (gente que olvidó fichar) con un guion
                            df_pivot = df_pivot.fillna('-')
                            
                            # Ordenamos por fecha para que el PDF quede cronológico
                            df_pivot['Fecha_sort'] = pd.to_datetime(df_pivot['Fecha_str'], format="%d/%m/%Y")
                            df_pivot = df_pivot.sort_values(by=['Fecha_sort', 'Empleado']).drop(columns=['Fecha_sort'])

                            st.write("Vista previa de los datos a exportar:")
                            st.dataframe(df_pivot, hide_index=True)
                            
                            # 4. Generación del PDF
                            pdf = FPDF()
                            pdf.add_page()
                            pdf.set_font("Arial", size=12)
                            
                            pdf.cell(200, 10, txt="Reporte de Asistencia - Estancia San Francisco", ln=True, align='C')
                            pdf.cell(200, 10, txt=f"Periodo: {fecha_inicio.strftime('%d/%m/%Y')} al {fecha_fin.strftime('%d/%m/%Y')}", ln=True, align='C')
                            pdf.ln(10)
                            
                            # Encabezados
                            pdf.set_font("Arial", 'B', 10)
                            pdf.cell(40, 10, "Fecha", border=1)
                            pdf.cell(60, 10, "Empleado", border=1)
                            pdf.cell(45, 10, "Hora Entrada", border=1)
                            pdf.cell(45, 10, "Hora Salida", border=1, ln=True)
                            
                            # Filas
                            pdf.set_font("Arial", '', 10)
                            for index, row in df_pivot.iterrows():
                                pdf.cell(40, 10, str(row['Fecha_str']), border=1)
                                pdf.cell(60, 10, str(row['Empleado']), border=1)
                                pdf.cell(45, 10, str(row['ENTRADA']), border=1)
                                pdf.cell(45, 10, str(row['SALIDA']), border=1, ln=True)
                            
                            pdf_output = pdf.output(dest='S').encode('latin-1')
                            
                            st.download_button(
                                label="⬇️ Descargar Reporte en PDF",
                                data=pdf_output,
                                file_name=f"Asistencia_{fecha_inicio}_al_{fecha_fin}.pdf",
                                mime="application/pdf"
                            )
