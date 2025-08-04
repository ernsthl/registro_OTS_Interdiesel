import streamlit as st
from PIL import Image
from database_mysql import conectar, crear_tabla, insertar_orden, obtener_ordenes, actualizar_estado, obtener_numeros_ot
from datetime import datetime
import pandas as pd


st.set_page_config(page_title="Control OT", layout="wide")
init_db()

logo = Image.open("logo_interdiesel.jpeg")  # o "assets/logo.png" si está en subcarpeta
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
st.image(logo, width=600)
st.markdown("</div>", unsafe_allow_html=True)

st.title("📋 Sistema de Control de Órdenes de Trabajo")

#clientes_opciones = ["TECNIBARRAGAN", "TOYOSERVICIOS", "OTRO"]
tecnicos_opciones = ["Escoja un técnico...","ARMANDO", "CHARLY", "GISELL", "SANTIAGO"]
estados_opciones = ["Escoja un Estado...", "DIAGNOSTICO", "COTIZADO", "AUTORIZADO", "DESPACHADO", "R-URG"]

# Inicializar session_state para limpiar campos
if "form_data" not in st.session_state:
    st.session_state["form_data"] = {
        "fecha_registro": datetime.now().date(),
        "numero_ot": "",
        "cliente": "",
        "tipo_servicio": "Escoja un servicio...",
        "tecnico": "Escoja un técnico...",
        "estado": "Escoja un Estado..."
    }

# Formulario de registro
with st.form("form_ot"):
    st.subheader("➕ Registrar nueva OT")
    col1, col2 = st.columns(2)
    with col1:
        fecha_registro = st.date_input("Fecha Registro OT", value=st.session_state["form_data"]["fecha_registro"])
        numero_ot = st.text_input("Número OT (Formato: OT-99999)", value=st.session_state["form_data"]["numero_ot"])
        cliente = st.text_input("Cliente", value=st.session_state["form_data"]["cliente"])
        tipo_servicio = st.selectbox("Tipo Servicio", ["Escoja un servicio...","LABORATORIO", "TALLER"], index=["Escoja un servicio...","LABORATORIO", "TALLER"].index(st.session_state["form_data"]["tipo_servicio"]))
    with col2:
        tecnico = st.selectbox("Técnico", tecnicos_opciones, index=tecnicos_opciones.index(st.session_state["form_data"]["tecnico"]))
        estado = st.selectbox("Estado OT", estados_opciones, index=estados_opciones.index(st.session_state["form_data"]["estado"]))
        if estado in ["AUTORIZADO", "R-URG"]:
            fecha_entrega = st.date_input("Fecha estimada de entrega")
            hora_entrega = st.time_input("Hora estimada de entrega")
        else:
            fecha_entrega = ""
            hora_entrega = ""
    submitted = st.form_submit_button("Registrar OT")

    if submitted:
        ot_existentes = obtener_numeros_ot()
        if numero_ot in ot_existentes:
            st.warning("⚠️ Ya existe una OT con ese número. Por favor usa otro número.")
        elif not numero_ot.strip():
            st.error("❌ El campo Número OT no puede estar vacío.")
        else:
            insertar_orden(str(fecha_registro), numero_ot, cliente, tipo_servicio, tecnico, estado, str(fecha_entrega), str(hora_entrega))
            st.success("✅ Orden registrada")

            # Limpiar formulario
            st.session_state["form_data"] = {
                "fecha_registro": datetime.now().date(),
                "numero_ot": " ",
                "cliente": " ",
                "tipo_servicio": "Escoja un servicio...",
                "tecnico": "Escoja un técnico...",
                "estado": "Escoja un Estado..."
            }
            st.rerun()

# Sección para actualizar estado
st.subheader("🔄 Cambiar estado de OT")
lista_ot = obtener_numeros_ot()
if lista_ot:
    ot_seleccionada = st.selectbox("Selecciona OT", lista_ot)
    nuevo_estado = st.selectbox("Nuevo estado", estados_opciones)
    if nuevo_estado in ["AUTORIZADO", "R-URG"]:
        nueva_fecha = st.date_input("Nueva fecha de entrega")
        nueva_hora = st.time_input("Nueva hora de entrega")
    else:
        nueva_fecha, nueva_hora = None, None
    if st.button("Actualizar estado"):
        actualizar_estado(ot_seleccionada, nuevo_estado, str(nueva_fecha) if nueva_fecha else None, str(nueva_hora) if nueva_hora else None)
        st.success(f"✅ OT {ot_seleccionada} actualizada")
        st.rerun()

# Tabla de órdenes con color por estado
st.subheader("📋 Órdenes de trabajo")
ordenes = obtener_ordenes()

df = pd.DataFrame(ordenes, columns=[
    "ID", "FECHA REGISTRO OT", "OT", "CLIENTE", "TIPO SERVICIO",
    "TECNICO", "ESTADO", "FECHA ENTREGA", "HORA ENTREGA"
])

df["COLOR ESTADO"] = df["ESTADO"].apply(lambda x: x.upper())

def colorear_estado(estado):
    colores = {
        "DIAGNOSTICO": "background-color: orange",
        "COTIZADO": "background-color: yellow",
        "AUTORIZADO": "background-color: lightgreen",
        "DESPACHADO": "background-color: lightblue",
        "R-URG": "background-color: red; color: white"
    }
    return colores.get(estado.upper(), "")

df_styled = df.style.map(colorear_estado, subset=["COLOR ESTADO"])
st.dataframe(df_styled, use_container_width=True)
