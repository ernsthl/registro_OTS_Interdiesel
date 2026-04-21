import streamlit as st
import pandas as pd
import json
from datetime import datetime
from database_mysql import (
    conectar, crear_tablas, insertar_orden, obtener_numeros_ot,
    actualizar_ot, verificar_credenciales, obtener_orden_por_numero, obtener_ordenes
)

# -------------------- Funciones auxiliares --------------------
def normalize_ot(num):
    if not num:
        return None
    s = str(num).strip()
    if s.lower().startswith("ot-"):
        s = s[3:].strip()
    if s == "":
        return None
    return f"OT-{s}"

def colorear_estado(val):
    colores = {
        "DIAGNÓSTICO": "background-color: orange",
        "COTIZADO": "background-color: yellow",
        "AUTORIZADO": "background-color: lightgreen",
        "DESPACHADO": "background-color: lightblue",
        "R-URG": "background-color: red; color: white"
    }
    return colores.get(str(val).upper(), "")

def registrar_cambio_ot():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("UPDATE log_sync SET last_update = NOW() WHERE id = 1")
    conn.commit()
    conn.close()

def actualizar_last_update_json():
    with open("last_update.json", "w") as f:
        json.dump({"last_update": datetime.now().isoformat()}, f)

# -------------------- Configuración inicial --------------------
st.set_page_config(page_title="Registro de OTs", layout="wide")
st.image("Logo_interdiesel.jpg", width=400)
crear_tablas()

st.markdown("## 🧾 Sistema de Control de Órdenes de Trabajo")
st.markdown("---")

# -------------------- Login --------------------
if "usuario" not in st.session_state:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🔐 Ingreso al sistema")
        usuario_input = st.text_input("👤 Usuario", placeholder="ingrese texto")
        contrasena_input = st.text_input("🔑 Contraseña", type="password", placeholder="ingrese texto")
        if st.button("➡️ Iniciar sesión"):
            if verificar_credenciales(usuario_input, contrasena_input):
                st.session_state.usuario = usuario_input
                st.success(f"✅ Bienvenido **{usuario_input}**")
                st.experimental_rerun()
            else:
                st.error("❌ Credenciales incorrectas")
    st.stop()

usuario = st.session_state["usuario"]

# -------------------- Registro de nueva OT --------------------
st.markdown("### ➕ Registro de nueva Orden de Trabajo")

with st.form("form_registro", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        fecha_registro = st.date_input("📅 Fecha de registro", value=datetime.now()).strftime("%Y-%m-%d")
        numero_ot_input = st.text_input("🔢 Número OT (solo número, ej. 9999)", placeholder="ingrese texto")
        cliente = st.text_input("👨‍💼 Cliente", placeholder="ingrese texto")
        marca_modelo = st.text_input("🚗 Marca y Modelo del Auto", placeholder="ingrese texto")
    with col2:
        tipo_servicio = st.selectbox("🛠️ Tipo de servicio", ["escoja una opción", "Laboratorio", "Taller"])
        tecnico = st.multiselect("👨‍🔧 Técnicos asignados", ["Armando", "Ronal", "Dario", "Gisell", "Santiago", "Externo"], default=[])
        estado = st.selectbox("📌 Estado", ["escoja una opción", "Diagnóstico", "Cotizado", "Autorizado", "Despachado", "R-URG"])

        if estado in ["Autorizado", "R-URG"]:
            fecha_entrega = st.date_input("📆 Fecha estimada de entrega")
            hora_entrega = st.time_input("🕓 Hora estimada de entrega")
        else:
            fecha_entrega, hora_entrega = None, None

    submitted = st.form_submit_button("📥 Registrar OT")

if submitted:
    numero_ot_full = normalize_ot(numero_ot_input)

    # Validar campos obligatorios
    if (not numero_ot_full 
        or tipo_servicio == "escoja una opción" 
        or estado == "escoja una opción"
        or not cliente.strip()
        or not marca_modelo.strip()
        or not tecnico  # si es multiselección
        or not fecha_registro):
        
        st.warning("⚠️ Complete todos los campos obligatorios.")
    
    else:
        existing_norm = [str(x).strip() for x in obtener_numeros_ot()]
        if numero_ot_full in existing_norm:
            st.error("🚫 El número de OT ya existe. Verifique.")
        else:
            try:
                insertar_orden(
                    fecha_registro,
                    numero_ot_full,
                    cliente,
                    marca_modelo,
                    tipo_servicio,
                    ", ".join(tecnico),
                    estado,
                    fecha_entrega.strftime("%Y-%m-%d") if fecha_entrega else None,
                    hora_entrega.strftime("%H:%M") if hora_entrega else None,
                    usuario
                )
                registrar_cambio_ot()
                actualizar_last_update_json()
                st.success("✅ Orden registrada exitosamente.")
            except Exception as e:
                st.error(f"Error al guardar OT: {e}")

st.markdown("---")

# -------------------- Actualizar OT --------------------
st.markdown("### ✏️ Actualizar OT")

num_busqueda = st.text_input("🔍 Ingrese número de OT para buscar", placeholder="ingrese texto")
if st.button("Buscar OT"):
    ot_data = obtener_orden_por_numero(normalize_ot(num_busqueda))
    if ot_data:
        st.session_state.ot_edit = ot_data
        st.success("OT encontrada. Puede editar los campos.")
    else:
        st.error("No se encontró la OT.")

if "ot_edit" in st.session_state:
    ot_edit = st.session_state.ot_edit

    # Estado y campos fecha/hora fuera del formulario para actualización dinámica
    estado = st.selectbox(
        "📌 Estado",
        ["Diagnóstico", "Cotizado", "Autorizado", "Despachado", "R-URG"],
        index=["Diagnóstico", "Cotizado", "Autorizado", "Despachado", "R-URG"].index(ot_edit["estado"]),
        key="estado_outside_form"
    )

    if estado in ["Autorizado", "R-URG"]:
        fecha_entrega = st.date_input(
            "📆 Fecha estimada de entrega",
            value=datetime.strptime(ot_edit["fecha_entrega"], "%Y-%m-%d") if ot_edit["fecha_entrega"] else datetime.now(),
            key="fecha_entrega_outside_form"
        )
        hora_entrega = st.time_input(
            "🕓 Hora estimada de entrega",
            value=datetime.strptime(ot_edit["hora_entrega"], "%H:%M").time() if ot_edit["hora_entrega"] else datetime.now().time(),
            key="hora_entrega_outside_form"
        )
    else:
        fecha_entrega = None
        hora_entrega = None

    with st.form("form_actualizar"):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Número OT:** {ot_edit['numero_ot']}")
            cliente = st.text_input("👨‍💼 Cliente", value=ot_edit["cliente"], key="cliente_form")
            marca_modelo = st.text_input("🚗 Marca y Modelo", value=ot_edit["marca_modelo"], key="marca_modelo_form")
            tipo_servicio = st.selectbox(
                "🛠️ Tipo de servicio",
                ["Laboratorio", "Taller"],
                index=0 if ot_edit["tipo_servicio"] == "Laboratorio" else 1,
                key="tipo_servicio_form"
            )
            tecnico = st.multiselect(
                "👨‍🔧 Técnicos asignados",
                ["Armando", "Ronal", "Dario", "Gisell", "Santiago", "Externo"],
                default=ot_edit["tecnico"].split(", "),
                key="tecnico_form"
            )
        with col2:
            st.write(f"**Fecha registro:** {ot_edit['fecha_registro']}")
            # No repetimos estado ni fecha/hora aquí porque están fuera

        if st.form_submit_button("💾 Guardar cambios"):
            try:
                actualizar_ot(
                    ot_edit["numero_ot"],
                    cliente,
                    marca_modelo,
                    tipo_servicio,
                    ", ".join(tecnico),
                    estado,
                    fecha_entrega.strftime("%Y-%m-%d") if fecha_entrega else None,
                    hora_entrega.strftime("%H:%M") if hora_entrega else None,
                    usuario
                )
                registrar_cambio_ot()
                actualizar_last_update_json()
                st.success("✅ OT actualizada exitosamente.")
                del st.session_state.ot_edit
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Error al actualizar OT: {e}")

st.markdown("---")

# -------------------- Listado de OTs --------------------
st.markdown("### 🖥️ Registro de Órdenes de Trabajo")
ordenes = obtener_ordenes()
if ordenes:
    df = pd.DataFrame(ordenes, columns=["ID","FECHA REGISTRO OT", "OT", "CLIENTE", "MARCA AUTO", "TIPO SERVICIO", "TECNICO", "ESTADO", "FECHA ENTREGA", "HORA ENTREGA", "USUARIO MODIFICACION", "FECHA MODIFICACION"])
    df_styled = df.style.applymap(colorear_estado, subset=["ESTADO"])
    st.dataframe(df_styled, use_container_width=True)
else:
    st.info("ℹ️ No hay OTs registradas aún.")
