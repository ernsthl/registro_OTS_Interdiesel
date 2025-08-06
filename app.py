
import streamlit as st
from datetime import datetime
from database_mysql import (
    crear_tablas, insertar_orden, obtener_numeros_ot,
    actualizar_estado, verificar_credenciales
)

st.set_page_config(page_title="Registro de OTs", layout="wide")
st.image("Logo_interdiesel.jpg", width=600)
crear_tablas()

st.markdown("## 🧾 Sistema de Control de Órdenes de Trabajo")
st.markdown("---")

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
    col1, col2, col3 = st.columns(3)
    with col1:
        fecha_registro = st.text_input("📅 Fecha de registro", value=datetime.now().strftime("%Y-%m-%d %H:%M"))
        numero_ot = st.text_input("🔢 Número OT")
        cliente = st.text_input("👨‍💼 Cliente")
    with col2:
        marca_modelo = st.text_input("🚗 Marca y Modelo del Auto")
        tipo_servicio = st.selectbox("🛠️ Tipo de servicio", ["Laboratorio", "Taller"])
        tecnico = st.multiselect("👨‍🔧 Técnicos asignados", ["Juan", "Carlos", "Diana", "Pedro"])
    with col3:
        estado = st.selectbox("📌 Estado", ["diagnóstico", "cotizado", "autorizado", "despachado", "R-URG"])
        fecha_entrega = st.date_input("📆 Fecha estimada de entrega")
        hora_entrega = st.time_input("🕓 Hora estimada de entrega")

    submitted = st.form_submit_button("📥 Registrar OT")

    if submitted:
        if numero_ot.strip() == "":
            st.warning("⚠️ Debe ingresar un número de OT.")
        elif numero_ot in obtener_numeros_ot():
            st.error("🚫 El número de OT ya existe. Verifique.")
        else:
            insertar_orden(
                fecha_registro, numero_ot, cliente, tipo_servicio,  ", ".join(tecnico), marca_modelo,
                estado, fecha_entrega.strftime("%Y-%m-%d"), hora_entrega.strftime("%H:%M"), usuario
            )
            st.success("✅ Orden registrada exitosamente.")
            st.experimental_rerun()

st.markdown("---")
st.markdown("### 🔄 Actualizar estado de OT existente")

# 🔄 Actualización de estado
numeros_ot = obtener_numeros_ot()
if numeros_ot:
    selected_ot = st.selectbox("🔍 Seleccionar OT", numeros_ot)
    nuevo_estado = st.selectbox("📝 Nuevo estado", ["diagnóstico", "cotizado", "autorizado", "despachado", "R-URG"])
    colf1, colf2 = st.columns(2)
    with colf1:
        nueva_fecha = st.date_input("📆 Nueva fecha estimada de entrega")
    with colf2:
        nueva_hora = st.time_input("🕓 Nueva hora estimada de entrega")

    if st.button("✅ Actualizar estado"):
        actualizar_estado(
            selected_ot,
            nuevo_estado,
            nueva_fecha.strftime("%Y-%m-%d"),
            nueva_hora.strftime("%H:%M"),
            usuario
        )
        st.success("🆗 Estado actualizado correctamente.")
        st.experimental_rerun()
else:
    st.info("ℹ️ No hay OTs registradas aún.")
