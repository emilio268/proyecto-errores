from flask import Flask, flash, Blueprint, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt, generate_password_hash, check_password_hash

# Crear una instancia de Flask
app = Flask(__name__)
app.secret_key = "VelaDanAik123"

# Configuración de SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/sistema'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

mysql = MySQL(app)
db = SQLAlchemy(app)

# Blueprint para el login
login_blueprint = Blueprint('login', __name__)

# ...

@login_blueprint.route('/acceso-login', methods=["GET", "POST"])
def login():
    _correo = None  # Definir _correo con un valor predeterminado
    if request.method == 'POST' and 'Usua_Correo' in request.form and 'Usua_Pass' in request.form:
        _correo = request.form['Usua_Correo']
        _password = request.form['Usua_Pass']

    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM usuarios WHERE Usua_Correo = %s', (_correo,))
    account = cur.fetchone()

    if account is not None and check_password_hash(account['Usua_Pass'], _password):
        # Si la contraseña coincide, realizar la autenticación y configurar la sesión
        session['Usua_Correo'] = _correo
        session['Usua_Nombre'] = account['Usua_Nombre']
        session['Usua_Id'] = account['Usua_Id']
        session['Usua_Foto'] = account['Usua_Foto']
        session['logueado'] = True  # Establece la sesión como autenticada

        # Incrementar el contador de inicios de sesión
        cur.execute("UPDATE usuarios SET Usua_IniciosSesion = Usua_IniciosSesion + 1 WHERE Usua_Id = %s", (account['Usua_Id'],))
        mysql.connection.commit()

        if account['Usua_Rol'] == 1:
            return redirect(url_for('mostrar_dashboardadmin'))
        elif account['Usua_Rol'] == 2:
            return redirect(url_for('mostrar_dashboardemp'))
        elif account['Usua_Rol'] == 3:
            return redirect(url_for('mostrar_dashboardcli'))
        elif account['Usua_Rol'] == 4:
            return redirect(url_for('mostrar_dashboardemp'))

    # Si la autenticación falla, mostrar un mensaje de error
    flash('Usuario o Contraseña Incorrectos', 'danger')

    return render_template('/login/login.html')

@login_blueprint.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        _correo = request.form['Usua_Correo']
        _contrasena = request.form['Usua_Pass']
        _nombre = request.form['Clie_Nombre']

        cur = mysql.connection.cursor()

        try:
            # Genera un hash seguro de la contraseña
            hashed_password = generate_password_hash(_contrasena).decode('utf-8')

            if _contrasena != request.form['confirm_Pass']:
                flash('Las contraseñas no coinciden', 'danger')
                return redirect(url_for('login.registro'))

            # Insertar en la tabla usuarios
            cur.execute("INSERT INTO usuarios (Usua_Correo, Usua_Pass, Usua_Nombre, Usua_IniciosSesion) VALUES (%s, %s, %s, 0)",
                        (_correo, hashed_password, _nombre))
            mysql.connection.commit()

            Usua_Id = cur.lastrowid

            # Insertar en la tabla clientes y establecer Clie_Correo
            cur.execute("INSERT INTO clientes (Clie_Nombre, Usua_Id, Clie_Correo) VALUES (%s, %s, %s)",
                        (_nombre, Usua_Id, _correo))
            mysql.connection.commit()

            cur.close()

            # Establecer la sesión como autenticada
            session['Usua_Correo'] = _correo
            session['logueado'] = True

            flash('Registro exitoso', 'success')

            # Redirigir al usuario según su rol después del registro
            cur.execute('SELECT Usua_Rol FROM usuarios WHERE Usua_Correo = %s', (_correo,))
            account = cur.fetchone()
            if account:
                if account['Usua_Rol'] == 1:
                    return render_template("/Dashboard-Admin/admin_Dashboard.html")
                elif account['Usua_Rol'] == 2:
                    return render_template("/Dashboard-Empleado/Emple-Dashboard.html")
                elif account['Usua_Rol'] == 3:
                    return render_template("/Dashboard-Cliente/clie-Dashboard.html")
                elif account['Usua_Rol'] == 4:
                    return render_template("/Dashboard-Empleado/Emple-Dashboard.html")

        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')

    return render_template('login/login.html')

@app.route('/proceso')
def proceso():
    return render_template('')

if __name__ == '__main__':
    app.run(debug=True)
