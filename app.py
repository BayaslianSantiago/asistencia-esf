import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
from fpdf import FPDF
import base64
import os

# --- 1. CONFIGURACIÓN DE PÁGINA Y CSS ---
st.set_page_config(
    page_title="Asistencia · Estancia San Francisco",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;600&family=Montserrat:wght@300;400;500;600&display=swap');

    /* ── BASE ── */
    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif;
        background-color: #0d0d0d;
        color: #e8e8e0;
    }
    .stApp { background-color: #0d0d0d; }

    /* ── ENCABEZADO ── */
    .header-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 2.5rem 0 1.5rem 0;
        border-bottom: 1px solid #2a2a2a;
        margin-bottom: 2rem;
    }
    .header-logo {
        width: 90px;
        margin-bottom: 1rem;
        filter: brightness(0) invert(1);
        opacity: 0.92;
    }
    .header-title {
        font-family: 'Cormorant Garamond', serif;
        font-size: 2.4rem;
        font-weight: 300;
        letter-spacing: 0.12em;
        color: #f0ece4;
        text-align: center;
        margin: 0;
        text-transform: uppercase;
    }
    .header-subtitle {
        font-size: 0.65rem;
        letter-spacing: 0.35em;
        color: #666;
        text-transform: uppercase;
        margin-top: 0.4rem;
        text-align: center;
    }

    /* ── SELECTBOX ── */
    div[data-baseweb="select"] > div {
        font-size: 15px;
        font-family: 'Montserrat', sans-serif;
        background-color: #161616 !important;
        border: 1px solid #2a2a2a !important;
        border-radius: 4px !important;
        color: #e8e8e0 !important;
    }
    label[data-testid="stWidgetLabel"] p {
        font-size: 0.7rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: #888;
        font-family: 'Montserrat', sans-serif;
    }

    /* ── DIVISOR ── */
    hr { border-color: #1e1e1e; margin: 1.5rem 0; }

    /* ── BOTONES ── */
    div.stButton > button {
        height: 110px;
        font-family: 'Montserrat', sans-serif;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.25em;
        text-transform: uppercase;
        border-radius: 4px;
        width: 100%;
        transition: all 0.25s ease;
        border: 1px solid #333;
        cursor: pointer;
    }
    div.stButton > button:hover { transform: translateY(-2px); }

    /* BOTÓN ENTRADA */
    div[data-testid="column"]:nth-of-type(1) div.stButton > button {
        background-color: #f0ece4;
        color: #0d0d0d;
        border: none;
        box-shadow: 0 4px 20px rgba(240, 236, 228, 0.1);
    }
    div[data-testid="column"]:nth-of-type(1) div.stButton > button:hover {
        background-color: #ffffff;
        box-shadow: 0 6px 28px rgba(255,255,255,0.15);
    }

    /* BOTÓN SALIDA */
    div[data-testid="column"]:nth-of-type(2) div.stButton > button {
        background-color: transparent;
        color: #e8e8e0;
        border: 1px solid #444;
    }
    div[data-testid="column"]:nth-of-type(2) div.stButton > button:hover {
        background-color: #1a1a1a;
        border-color: #888;
    }

    /* ── ALERTAS ── */
    div[data-testid="stAlert"] {
        border-radius: 4px;
        font-family: 'Montserrat', sans-serif;
        font-size: 0.82rem;
        letter-spacing: 0.03em;
    }

    /* ── SIDEBAR ── */
    [data-testid="stSidebar"] {
        background-color: #111 !important;
        border-right: 1px solid #1e1e1e;
    }
    [data-testid="stSidebar"] * { font-family: 'Montserrat', sans-serif !important; }
    [data-testid="stSidebar"] h3 {
        font-family: 'Cormorant Garamond', serif !important;
        font-size: 1.2rem;
        letter-spacing: 0.1em;
        color: #ccc;
        font-weight: 400;
    }

    /* ── DATAFRAME ── */
    [data-testid="stDataFrame"] {
        border: 1px solid #1e1e1e;
        border-radius: 4px;
    }
    </style>
""", unsafe_allow_html=True)


# --- 2. ENCABEZADO CON LOGO ---
logo_path = "logo.png"
logo_html = ""
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode()
    logo_html = f'<img src="data:image/png;base64,{logo_b64}" class="header-logo"/>'

st.markdown(f"""
    <div class="header-container">
        {logo_html}
        <h1 class="header-title">Estancia San Francisco</h1>
        <p class="header-subtitle">Registro de Asistencia del Personal</p>
    </div>
""", unsafe_allow_html=True)


# --- 3. CONEXIÓN A GOOGLE SHEETS ---
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


# --- 4. INTERFAZ Y LÓGICA DE FICHADA ---
empleados = [
    "Seleccionar...",
    "Brian", "Erika", "Fernanda", "Juliera",
    "Mariel", "Oriana", "Santiago"
]

nombre = st.selectbox("Empleado", empleados)

if nombre != "Seleccionar...":
    st.write("---")
    col1, col2 = st.columns(2, gap="medium")
    zona_ar = ZoneInfo("America/Argentina/Buenos_Aires")

    with col1:
        if st.button("↑  Entrada", use_container_width=True):
            ahora = datetime.now(zona_ar)
            fecha_hoy = ahora.strftime("%d/%m/%Y")
            hora_actual = ahora.strftime("%d/%m/%Y %H:%M:%S")

            datos = hoja_asistencia.get_all_records()
            ya_ficho = False
            if datos:
                df = pd.DataFrame(datos)
                filtro = (
                    df['Fecha y Hora'].str.startswith(fecha_hoy) &
                    (df['Empleado'] == nombre) &
                    (df['Acción'] == 'ENTRADA')
                )
                if not df[filtro].empty:
                    ya_ficho = True

            if ya_ficho:
                st.error(f"⚠️ {nombre}, ya registraste tu entrada hoy.")
            else:
                hoja_asistencia.append_row([hora_actual, nombre, "ENTRADA"])
                st.success(f"✓ Entrada registrada — {nombre} · {hora_actual}")

    with col2:
        if st.button("↓  Salida", use_container_width=True):
            ahora = datetime.now(zona_ar)
            fecha_hoy = ahora.strftime("%d/%m/%Y")
            hora_actual = ahora.strftime("%d/%m/%Y %H:%M:%S")

            datos = hoja_asistencia.get_all_records()
            ya_ficho = False
            if datos:
                df = pd.DataFrame(datos)
                filtro = (
                    df['Fecha y Hora'].str.startswith(fecha_hoy) &
                    (df['Empleado'] == nombre) &
                    (df['Acción'] == 'SALIDA')
                )
                if not df[filtro].empty:
                    ya_ficho = True

            if ya_ficho:
                st.error(f"⚠️ {nombre}, ya registraste tu salida hoy.")
            else:
                hoja_asistencia.append_row([hora_actual, nombre, "SALIDA"])
                st.warning(f"✓ Salida registrada — {nombre} · {hora_actual}")


# --- 5. PANEL DE ADMINISTRACIÓN (SIDEBAR) ---
with st.sidebar:
    st.markdown("### ⚙ Administración")
    clave_ingresada = st.text_input("Clave de acceso:", type="password")

    if clave_ingresada == st.secrets["general"]["admin_password"]:
        st.success("Acceso concedido")
        st.markdown("---")

        rango_fechas = st.date_input("Período a exportar:", [])

        if len(rango_fechas) == 2:
            fecha_inicio, fecha_fin = rango_fechas

            if st.button("Generar PDF", use_container_width=True):
                with st.spinner("Procesando datos..."):
                    datos = hoja_asistencia.get_all_records()

                    if not datos:
                        st.warning("No hay registros todavía.")
                    else:
                        df = pd.DataFrame(datos)
                        df['Datetime'] = pd.to_datetime(df['Fecha y Hora'], format="%d/%m/%Y %H:%M:%S")
                        df['Fecha_str'] = df['Datetime'].dt.strftime('%d/%m/%Y')
                        df['Hora_str'] = df['Datetime'].dt.strftime('%H:%M')
                        df['Solo_Fecha'] = df['Datetime'].dt.date

                        mask = (df['Solo_Fecha'] >= fecha_inicio) & (df['Solo_Fecha'] <= fecha_fin)
                        df_filtrado = df.loc[mask].copy()

                        if df_filtrado.empty:
                            st.info("No hay registros para este período.")
                        else:
                            df_pivot = df_filtrado.pivot_table(
                                index=['Fecha_str', 'Empleado'],
                                columns='Acción',
                                values='Hora_str',
                                aggfunc='first'
                            ).reset_index()

                            if 'ENTRADA' not in df_pivot.columns: df_pivot['ENTRADA'] = '-'
                            if 'SALIDA' not in df_pivot.columns: df_pivot['SALIDA'] = '-'
                            df_pivot = df_pivot.fillna('-')

                            df_pivot['Fecha_sort'] = pd.to_datetime(df_pivot['Fecha_str'], format="%d/%m/%Y")
                            df_pivot = df_pivot.sort_values(['Fecha_sort', 'Empleado']).drop(columns=['Fecha_sort'])

                            st.write("Vista previa:")
                            st.dataframe(df_pivot, hide_index=True)

                            # ── GENERACIÓN PDF ELEGANTE ──
                            pdf = FPDF()
                            pdf.set_margins(18, 18, 18)
                            pdf.add_page()
                            page_w = pdf.w - 36  # ancho útil (márgenes 18+18)

                            # Encabezado: logo + título
                            if os.path.exists(logo_path):
                                pdf.image(logo_path, x=18, y=14, h=18)
                                pdf.set_xy(18, 14)

                            pdf.set_font("Helvetica", 'B', 18)
                            pdf.set_text_color(15, 15, 15)
                            pdf.cell(page_w, 10, "ESTANCIA SAN FRANCISCO", align='C')
                            pdf.ln(8)

                            pdf.set_font("Helvetica", '', 8)
                            pdf.set_text_color(120, 120, 120)
                            pdf.cell(page_w, 6,
                                     f"REPORTE DE ASISTENCIA  ·  {fecha_inicio.strftime('%d/%m/%Y')} — {fecha_fin.strftime('%d/%m/%Y')}",
                                     align='C')
                            pdf.ln(4)

                            # Línea divisoria doble
                            pdf.set_draw_color(15, 15, 15)
                            pdf.set_line_width(0.7)
                            pdf.line(18, pdf.get_y(), pdf.w - 18, pdf.get_y())
                            pdf.ln(0.5)
                            pdf.set_line_width(0.2)
                            pdf.line(18, pdf.get_y(), pdf.w - 18, pdf.get_y())
                            pdf.ln(7)

                            # Anchos de columnas
                            col_fecha   = 38
                            col_emp     = 68
                            col_entrada = 37
                            col_salida  = 37

                            # Encabezados de tabla
                            pdf.set_fill_color(15, 15, 15)
                            pdf.set_text_color(245, 245, 240)
                            pdf.set_font("Helvetica", 'B', 8)
                            row_h = 9
                            pdf.set_line_width(0)

                            for txt, w in [("FECHA", col_fecha), ("EMPLEADO", col_emp),
                                           ("ENTRADA", col_entrada), ("SALIDA", col_salida)]:
                                pdf.cell(w, row_h, txt, border=0, fill=True, align='C')
                            pdf.ln(row_h)

                            # Filas alternadas
                            pdf.set_font("Helvetica", '', 9)
                            pdf.set_line_width(0.1)

                            for i, (_, row) in enumerate(df_pivot.iterrows()):
                                # Fondo alternado
                                if i % 2 == 0:
                                    pdf.set_fill_color(255, 255, 255)
                                else:
                                    pdf.set_fill_color(245, 245, 243)

                                pdf.set_text_color(30, 30, 30)
                                pdf.set_draw_color(210, 210, 205)

                                pdf.cell(col_fecha,   row_h, str(row['Fecha_str']), border='B', fill=True, align='C')
                                pdf.cell(col_emp,     row_h, str(row['Empleado']),  border='B', fill=True, align='L')
                                pdf.cell(col_entrada, row_h, str(row['ENTRADA']),   border='B', fill=True, align='C')
                                pdf.cell(col_salida,  row_h, str(row['SALIDA']),    border='B', fill=True, align='C')
                                pdf.ln(row_h)

                            # Línea de cierre
                            pdf.set_draw_color(15, 15, 15)
                            pdf.set_line_width(0.5)
                            pdf.line(18, pdf.get_y(), pdf.w - 18, pdf.get_y())
                            pdf.ln(5)

                            # Total de registros
                            pdf.set_font("Helvetica", 'I', 7.5)
                            pdf.set_text_color(140, 140, 140)
                            pdf.cell(page_w, 6,
                                     f"Total de registros: {len(df_pivot)}  ·  Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                                     align='R')

                            pdf_output = pdf.output(dest='S').encode('latin-1')

                            st.download_button(
                                label="⬇ Descargar Reporte PDF",
                                data=pdf_output,
                                file_name=f"Asistencia_{fecha_inicio}_al_{fecha_fin}.pdf",
                                mime="application/pdf"
                            )
