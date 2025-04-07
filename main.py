from flask import Flask, render_template, request, redirect, url_for
from flask_paginate import Pagination, get_page_parameter
from flask_login import LoginManager, login_required
import mysql.connector

app = Flask(__name__)
app.secret_key = 'una_clave_secreta_segura'  # Necesario para Flask-Login

#accesos a la base de datos  
"""
user
'lector_pvuela'
pass
'Lector2024!'
'host='45.162.168.163',
'database='PVUELA'
"""
#
#


# --- Configuración de Flask-Login ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # Ruta a la que redirige si no estás logueado

# --- Conexión a MySQL ---
def connect_to_mysql(user, password, host, database):
    connection = mysql.connector.connect(
        user=user,
        password=password,
        host=host.strip(),
        database=database
    )
    return connection

# --- Ruta protegida con paginación ---
@app.route("/giftcards")
@login_required
def giftcards():
    connection = connect_to_mysql(
        user='',
        password='',
        host='45.162.168.163',
        database='PVUELA'
    )
    cursor = connection.cursor()

    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 10
    offset = (page - 1) * per_page

    cursor.execute("SELECT * FROM tarjetas LIMIT %s OFFSET %s", (per_page, offset))
    columns = [column[0] for column in cursor.description]
    tarjetas = [dict(zip(columns, row)) for row in cursor.fetchall()]

    # Obtener el total real de registros
    cursor.execute("SELECT COUNT(*) FROM tarjetas")
    total = cursor.fetchone()[0]

    cursor.close()
    connection.close()

    pagination = Pagination(page=page, total=total, per_page=per_page, css_framework='bootstrap4')

    return render_template("tarjetas.html", tarjetas=tarjetas, pagination=pagination)

if __name__ == "__main__":
    app.run(debug=True)
