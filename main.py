from flask import Flask, render_template, request, redirect, url_for
from flask_paginate import Pagination, get_page_parameter
from flask_login import LoginManager, login_required
import mysql.connector
from datetime import datetime, timedelta

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


@app.route("/reportes")
@login_required
def reports():
    return render_template("reporte.html")


@app.route("/reporte_paquetes")
@login_required
def package_report():
    global cursor, connection
    current_date = datetime.now().strftime('%Y-%m-%d')
    start_default = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')
    start_date = request.args.get('fecha_inicio', start_default)
    end_date = request.args.get('fecha_fin', current_date)

    try:
        connection = connect_to_mysql(
            user='',
            password='',
            host='45.162.168.163',
            database='PVUELA'
        )
        cursor = connection.cursor()

        query = '''
                SELECT paquete as description, COUNT(paquete) as sales
                FROM ventas
                WHERE fecha BETWEEN %s AND %s
                AND paquete IS NOT NULL
                GROUP BY paquete
                ORDER BY COUNT(paquete) DESC;
            '''

        cursor.execute(query, (start_date, end_date))
        columns = [column[0] for column in cursor.description]
        packages = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return render_template("reportes_paquetes.html", packages=packages)
    except mysql.connector.Error as err:
        return f"Database error: {err}", 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection:
            connection.close()


@app.route("/reporte_metodos_pago")
@login_required
def payment_methods_report():
    global cursor, connection
    current_date = datetime.now().strftime('%Y-%m-%d')
    start_default = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')
    start_date = request.args.get('fecha_inicio', start_default)
    end_date = request.args.get('fecha_fin', current_date)

    try:
        connection = connect_to_mysql(
            user='',
            password='',
            host='45.162.168.163',
            database='PVUELA'
        )
        cursor = connection.cursor()

        query = '''
                SELECT
                    SUM(efectivo) AS total_cash,
                    SUM(transferencia) AS total_transfer,
                    SUM(dolar) AS total_dollar,
                    SUM(tarjetamtd) AS total_card
                FROM ventas
                WHERE fecha BETWEEN %s AND %s
                '''

        cursor.execute(query, (start_date, end_date))
        columns = [column[0] for column in cursor.description]
        payment_methods = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return render_template("reportes_metodos_pago.html", payment_methods=payment_methods)
    except mysql.connector.Error as err:
        return f"Database error: {err}", 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection:
            connection.close()


@app.route("/reporte_minutos")
@login_required
def minutes_report():
    global cursor, connection
    current_date = datetime.now().strftime('%Y-%m-%d')
    start_default = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')
    start_date = request.args.get('fecha_inicio', start_default)
    end_date = request.args.get('fecha_fin', current_date)

    try:
        connection = connect_to_mysql(
            user='',
            password='',
            host='45.162.168.163',
            database='PVUELA'
        )
        cursor = connection.cursor()

        query = '''
                SELECT
                    SUM(minutos) AS total
                FROM ventas
                WHERE fecha BETWEEN %s AND %s
                '''

        cursor.execute(query, (start_date, end_date))
        result = cursor.fetchone()
        total = result[0] if result[0] is not None else 0
        return render_template("reportes_minutos.html", total=total)
    except mysql.connector.Error as err:
        return f"Database error: {err}", 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection:
            connection.close()


@app.route("/reporte_gastos")
@login_required
def expense_report():
    global cursor, connection
    current_date = datetime.now().strftime('%Y-%m-%d')
    start_default = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')
    start_date = request.args.get('fecha_inicio', start_default)
    end_date = request.args.get('fecha_fin', current_date)

    try:
        connection = connect_to_mysql(
            user='',
            password='',
            host='45.162.168.163',
            database='PVUELA'
        )
        cursor = connection.cursor()

        query = '''
                SELECT fecha, descripcion, monto
                FROM gastos
                WHERE fecha BETWEEN %s AND %s
                    AND descripcion IS NOT NULL
                ORDER BY fecha DESC;
                '''

        cursor.execute(query, (start_date, end_date))
        columns = [column[0] for column in cursor.description]
        expenses = [dict(zip(columns, row)) for row in cursor.fetchall()]
        total_amount = sum(int(expense['monto']) for expense in expenses)
        return render_template("reportes_gastos.html", expenses=expenses, total_amount=total_amount)
    except mysql.connector.Error as err:
        return f"Database error: {err}", 500
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'connection' in locals() and connection:
            connection.close()


if __name__ == "__main__":
    app.run(debug=True)
