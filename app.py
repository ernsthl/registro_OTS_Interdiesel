
import streamlit as st
from datetime import datetime
from database_mysql import (
    crear_tablas, insertar_orden, obtener_numeros_ot,
    actualizar_estado, verificar_credenciales
)

st.set_page_config(page_title="Registro de OTs", layout="wide")

# Crear tablas al iniciar
crear_tablas()

# Login
if "usuario" not in st.session_state:
    st.title("Ingreso al sistema")
    usuario_input = st.text_input("Usuario")
    contrasena_input = st.text_input("Contraseña", type="password")
    if st.button("Iniciar sesión"):
        if verificar_credenciales(usuario_input, contrasena_input):
            st.session_state.usuario = usuario_input
            st.success(f"Bienvenido {usuario_input}")
            st.experimental_rerun()
        else:
            st.error("Credenciales incorrectas")
    st.stop()

st.title("Registro de Órdenes de Trabajo")
usuario = st.session_state["usuario"]

# Formulario
with st.form("form_registro"):
    col1, col2, col3 = st.columns(3)
    with col1:
        fecha_registro = st.text_input("Fecha de registro OT", value=datetime.now().strftime("%Y-%m-%d %H:%M"))
        numero_ot = st.text_input("Número OT")
        cliente = st.text_input("Cliente")
        marca_modelo = st.text_input("Marca y Modelo del Auto")
    with col2:
        tipo_servicio = st.selectbox("Tipo de servicio", ["Laboratorio", "Taller"])
        tecnico = st.selectbox("Nombre del técnico", ["Juan", "Carlos", "Diana", "Pedro"])
        estado = st.selectbox("Estado", ["diagnóstico", "cotizado", "autorizado", "despachado", "R-URG"])
    with col3:
        fecha_entrega = st.date_input("Fecha estimada de entrega")
        hora_entrega = st.time_input("Hora estimada de entrega")

    submitted = st.form_submit_button("Registrar OT")

    if submitted:
        if numero_ot.strip() == "":
            st.warning("Debe ingresar un número de OT.")
        elif numero_ot in obtener_numeros_ot():
            st.error("Ese número de OT ya existe.")
        else:
            insertar_orden(
                fecha_registro, numero_ot, cliente, tipo_servicio, tecnico,
                estado, fecha_entrega.strftime("%Y-%m-%d"), hora_entrega.strftime("%H:%M"), usuario
            )
            st.success("Orden registrada exitosamente.")
            st.experimental_rerun()

# Actualización de estado
st.subheader("Actualizar estado de una OT existente")
numeros_ot = obtener_numeros_ot()
if numeros_ot:
    selected_ot = st.selectbox("Seleccionar OT", numeros_ot)
    nuevo_estado = st.selectbox("Nuevo estado", ["diagnóstico", "cotizado", "autorizado", "despachado", "R-URG"])
    colf1, colf2 = st.columns(2)
    with colf1:
        nueva_fecha = st.date_input("Nueva fecha estimada de entrega")
    with colf2:
        nueva_hora = st.time_input("Nueva hora estimada de entrega")

    if st.button("Actualizar estado"):
        actualizar_estado(
            selected_ot,
            nuevo_estado,
            nueva_fecha.strftime("%Y-%m-%d"),
            nueva_hora.strftime("%H:%M"),
            usuario
        )
        st.success("Estado actualizado correctamente.")
        st.experimental_rerun()
else:
    st.info("No hay OTs registradas aún.")
