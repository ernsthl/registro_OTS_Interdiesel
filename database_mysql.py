
import mysql.connector

def conectar():
    return mysql.connector.connect(
        host="us-phx-web1166.main-hosting.eu",
        user="u978404744_admin",
        password="91AW9S:IPj&",
        database="u978404744_control_ots"
    )
