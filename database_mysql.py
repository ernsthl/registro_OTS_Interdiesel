
import mysql.connector

def conectar():
    return mysql.connector.connect(
        host="us-phx-web1166.main-hosting.eu",
        user="u978404744_admin",
        password="91AW9S:IPj&",
        database="u978404744_control_ots"
    )

def crear_tabla():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS orden_trabajo (
            id INT AUTO_INCREMENT PRIMARY KEY,
            fecha_registro VARCHAR(50),
            numero_ot VARCHAR(50) UNIQUE,
            cliente VARCHAR(100),
            tipo_servicio VARCHAR(50),
            tecnico VARCHAR(50),
            estado VARCHAR(50),
            fecha_entrega VARCHAR(50),
            hora_entrega VARCHAR(50)
        )
    """)
    conn.commit()
    conn.close()

def insertar_orden(fecha_registro, numero_ot, cliente, tipo_servicio, tecnico, estado, fecha_entrega, hora_entrega):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO orden_trabajo (fecha_registro, numero_ot, cliente, tipo_servicio, tecnico, estado, fecha_entrega, hora_entrega)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (fecha_registro, numero_ot, cliente, tipo_servicio, tecnico, estado, fecha_entrega, hora_entrega))
    conn.commit()
    conn.close()

def obtener_ordenes():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM orden_trabajo ORDER BY fecha_registro DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

def actualizar_estado(numero_ot, nuevo_estado, nueva_fecha=None, nueva_hora=None):
    conn = conectar()
    cur = conn.cursor()
    if nueva_fecha and nueva_hora:
        cur.execute("""
            UPDATE orden_trabajo SET estado = %s, fecha_entrega = %s, hora_entrega = %s WHERE numero_ot = %s
        """, (nuevo_estado, nueva_fecha, nueva_hora, numero_ot))
    else:
        cur.execute("""
            UPDATE orden_trabajo SET estado = %s WHERE numero_ot = %s
        """, (nuevo_estado, numero_ot))
    conn.commit()
    conn.close()

def obtener_numeros_ot():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT numero_ot FROM orden_trabajo ORDER BY fecha_registro DESC")
    rows = cur.fetchall()
    conn.close()
    return [row[0] for row in rows]
