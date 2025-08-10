
import streamlit as st
from datetime import datetime, time
from database_mysql import (
    crear_tablas, insertar_orden, obtener_numeros_ot,
    actualizar_estado, verificar_credenciales, obtener_ordenes
)

def normalize_ot(num):
    """Recibe lo que ingresó el usuario y devuelve 'OT-xxxxx' o None si está vacío."""
    if not num:
        return None
    s = str(num).strip()
    # Si empieza con ot- o OT-, quitar prefijo y usar la parte numérica
    if s.lower().startswith("ot-"):
        s = s[3:].strip()
    if s == "":
        return None
    return f"OT-{s}"
    
st.set_page_config(page_title="Registro de OTs", layout="wide")
st.image("Logo_interdiesel.jpg", width=600)
crear_tablas()

st.markdown("## 🧾 Sistema de Control de Órdenes de Trabajo")
st.markdown("---")

# 🔐 Login
if "usuario" not in st.session_state:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🔐 Ingreso al sistema")
        usuario_input = st.text_input("👤 Usuario")
        contrasena_input = st.text_input("🔑 Contraseña", type="password")
        if st.button("➡️ Iniciar sesión"):
            if verificar_credenciales(usuario_input, contrasena_input):
                st.session_state.usuario = usuario_input
                st.success(f"✅ Bienvenido **{usuario_input}**")
                st.experimental_rerun()
            else:
                st.error("❌ Credenciales incorrectas")
    st.stop()

usuario = st.session_state["usuario"]

# ➕ Registro de OTs
st.markdown("### ➕ Registro de nueva Orden de Trabajo")

with st.form("form_registro"):
    col1, col2 = st.columns(2)
    with col1:
        fecha_registro = st.date_input("📅 Fecha de registro", value=datetime.now()).strftime("%Y-%m-%d")
        numero_ot_input = st.text_input("🔢 Número OT (ingresa solo el número, ej. 9999)")
        cliente = st.text_input("👨‍💼 Cliente")
        marca_modelo = st.text_input("🚗 Marca y Modelo del Auto")
    with col2:
        tipo_servicio = st.selectbox("🛠️ Tipo de servicio", ["Laboratorio", "Taller"])
        tecnico = st.multiselect("👨‍🔧 Técnicos asignados", ["Armando", "Charly", "Dario", "Guiselle", "Santiago"])
        estado = st.selectbox("📌 Estado", ["Diagnóstico", "Cotizado", "Autorizado", "Despachado", "R-URG"])

        if estado == "autorizado":
            fecha_entrega = st.date_input("📆 Fecha estimada de entrega")
            hora_entrega = st.time_input("🕓 Hora estimada de entrega")
        else:
            fecha_entrega = None
            hora_entrega = None

    submitted = st.form_submit_button("📥 Registrar OT")

    tecnico_txt = ", ".join(tecnico)

if submitted:
    numero_ot_full = normalize_ot(numero_ot_input)
    if not numero_ot_full:
        st.warning("⚠️ Debe ingresar un número de OT.")
    else:
        existing = obtener_numeros_ot()
        # normalizar lista existente por si acaso (por seguridad)
        existing_norm = [str(x).strip() for x in existing]
        if numero_ot_full in existing_norm:
            st.error("🚫 El número de OT ya existe. Verifique.")
        else:
            try:
                insertar_orden(
                    fecha_registro,
                    numero_ot_full,
                    cliente,
                    marca_modelo,
                    ", ".join(tipo_servicio) if isinstance(tipo_servicio, list) else tipo_servicio,
                    ", ".join(tecnico) if isinstance(tecnico, list) else tecnico,
                    estado.strip().lower(),
                    fecha_entrega.strftime("%Y-%m-%d") if fecha_entrega else None,
                    hora_entrega.strftime("%H:%M") if hora_entrega else None,
                    usuario
                )
                st.success("✅ Orden registrada exitosamente.")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Error al guardar OT: {e}")
                
st.markdown("---")
st.markdown("### 🔄 Actualizar estado de OT existente")

# 🔄 Actualización de estado
numeros_ot = obtener_numeros_ot()
if numeros_ot:
    selected_ot = st.selectbox("🔍 Seleccionar OT", numeros_ot)
    nuevo_estado = st.selectbox("📝 Nuevo estado", ["Diagnóstico", "Cotizado", "Autorizado", "Despachado", "R-URG"])
    if nuevo_estado in ["Autorizado", "R-URG"]:
        nueva_fecha = st.date_input("📆 Nueva fecha estimada de entrega")
        nueva_hora = st.time_input("🕓 Nueva hora estimada de entrega")
    else:
        nueva_fecha, nueva_hora = None, None

if st.button("✅ Actualizar estado"):
    fecha_str = nueva_fecha.strftime("%Y-%m-%d") if nueva_fecha else None
    hora_str = nueva_hora.strftime("%H:%M") if nueva_hora else None

    actualizar_estado(
        selected_ot,
        nuevo_estado,
        fecha_str,
        hora_str,
        usuario
    )
    st.success("🆗 Estado actualizado correctamente.")
    st.experimental_rerun()
else:
    st.info("ℹ️ No hay OTs registradas aún.")

st.subheader("📋 Órdenes de trabajo")
ordenes = obtener_ordenes()

def colorear_estado(estado):
    colores = {
        "Diagnóstico": "background-color: orange",
        "Cotizado": "background-color: yellow",
        "Autorizado": "background-color: lightgreen",
        "Despachado": "background-color: lightblue",
        "R-URG": "background-color: red; color: white"
    }
    return colores.get(estado.upper(), "")

import pandas as pd
df = pd.DataFrame(ordenes, columns=["ID","FECHA REGISTRO OT", "OT", "CLIENTE", "MARCA AUTO", "TIPO SERVICIO", "TECNICO", "ESTADO", "FECHA ENTREGA", "HORA ENTREGA"])
df["COLOR ESTADO"] = df["ESTADO"].apply(lambda x: x.upper())
df_styled = df.style.applymap(colorear_estado, subset=["COLOR ESTADO"])

st.dataframe(df_styled, use_container_width=True)
