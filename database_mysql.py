
import mysql.connector
from datetime import datetime

def conectar():
    return mysql.connector.connect(
        host="us-phx-web1166.main-hosting.eu",
        user="u978404744_admin",
        password="91AW9S:IPj&",
        database="u978404744_control_ots"
    )

def crear_tablas():
    conn = conectar()
    cur = conn.cursor()

    # Tabla principal
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orden_trabajo (
            id INT AUTO_INCREMENT PRIMARY KEY,
            fecha_registro VARCHAR(50),
            numero_ot VARCHAR(50) UNIQUE,
            cliente VARCHAR(100),
            marca_modelo VARCHAR(100),
            tipo_servicio VARCHAR(50),
            tecnico VARCHAR(50),
            estado VARCHAR(50),
            fecha_entrega VARCHAR(50),
            hora_entrega VARCHAR(50)
        )
    """)

    # Tabla de sincronización
    cur.execute("""
        CREATE TABLE IF NOT EXISTS log_sync (
            id INT PRIMARY KEY,
            last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
    """)
    cur.execute("INSERT IGNORE INTO log_sync (id) VALUES (1)")

    # Tabla de auditoría
    cur.execute("""
        CREATE TABLE IF NOT EXISTS log_auditoria (
            id INT AUTO_INCREMENT PRIMARY KEY,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            operacion VARCHAR(20),
            numero_ot VARCHAR(50),
            estado_anterior VARCHAR(50),
            estado_nuevo VARCHAR(50),
            usuario TEXT
        )
    """)

    # Tabla de usuarios
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre_usuario VARCHAR(50) UNIQUE,
            contrasena VARCHAR(100)
        )
    """)
    cur.execute("INSERT IGNORE INTO usuarios (nombre_usuario, contrasena) VALUES ('admin', '567admin.'), ('operador', 'ot2025')")

    conn.commit()
    conn.close()

def verificar_credenciales(usuario, contrasena):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM usuarios WHERE nombre_usuario = %s AND contrasena = %s", (usuario, contrasena))
    result = cur.fetchone()
    conn.close()
    return result is not None

def insertar_orden(fecha_registro, numero_ot_full, cliente, marca_modelo, tipo_servicio, tecnico, estado, fecha_entrega, hora_entrega, usuario):
    if isinstance(tecnico, list):
        tecnico = ", ".join(tecnico)
        
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO orden_trabajo (fecha_registro, numero_ot, cliente, marca_modelo, tipo_servicio, tecnico, estado, fecha_entrega, hora_entrega)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (fecha_registro, numero_ot_full, cliente, marca_modelo, tipo_servicio, tecnico, estado, fecha_entrega, hora_entrega))

    # Auditoría
    cur.execute("""
        INSERT INTO log_auditoria (operacion, numero_ot, estado_anterior, estado_nuevo, usuario)
        VALUES (%s, %s, %s, %s, %s)
    """, ("registro", numero_ot_full, None, estado, usuario))

    # Actualizar log_sync
    cur.execute("UPDATE log_sync SET last_update = NOW() WHERE id = 1")

    conn.commit()
    conn.close()

def obtener_ordenes():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM orden_trabajo ORDER BY fecha_registro DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

def obtener_ordenes_pantalla():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT numero_ot, fecha_registro, cliente, marca_modelo, tipo_servicio, tecnico, estado, fecha_entrega, hora_entrega FROM orden_trabajo where estado != 'Despachado' ORDER BY fecha_registro DESC")
    rows = cur.fetchall()
    conn.close()
    return rows
    
def obtener_orden_por_numero(numero_ot):
    conn = conectar()
    cur = conn.cursor()
    try:
        conn = conectar()
        cursor = conn.cursor(dictionary=True)  # Retorna filas como diccionario

        sql = "SELECT * FROM orden_trabajo WHERE numero_ot = %s"
        cursor.execute(sql, (numero_ot,))
        resultado = cursor.fetchone()  # Solo una fila

        return resultado  # Diccionario o None si no encontró

    except Exception as e:
        raise Exception(f"Error obteniendo OT: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            
def actualizar_ot(numero_ot_full, cliente, marca_modelo, tipo_servicio, tecnico, estado, fecha_entrega, hora_entrega, usuario):
    conn = None
    cursor = None
    try:
        conn = conectar()
        cursor = conn.cursor()

        campos = [
            "cliente = %s",
            "marca_modelo = %s",
            "tipo_servicio = %s",
            "tecnico = %s",
            "estado = %s",
            "usuario_modificacion = %s",
            "fecha_modificacion = NOW()"
        ]

        valores = [cliente, marca_modelo, tipo_servicio, tecnico, estado, usuario]

        if fecha_entrega is not None:
            campos.append("fecha_entrega = %s")
            valores.append(fecha_entrega)

        if hora_entrega is not None:
            campos.append("hora_entrega = %s")
            valores.append(hora_entrega)

        sql = f"UPDATE orden_trabajo SET {', '.join(campos)} WHERE numero_ot = %s"
        valores.append(numero_ot_full)

        cursor.execute(sql, valores)
        conn.commit()

    except Exception as e:
        raise Exception(f"Error actualizando OT: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def obtener_numeros_ot():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT numero_ot FROM orden_trabajo ORDER BY fecha_registro DESC")
    rows = cur.fetchall()
    conn.close()
    return [row[0] for row in rows]

def obtener_timestamp_sync():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT last_update FROM log_sync WHERE id = 1")
    result = cur.fetchone()
    conn.close()
    return result[0] if result else None
