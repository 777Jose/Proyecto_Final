from flask import Blueprint, render_template, redirect, url_for, session, request
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from functools import wraps

login_bp = Blueprint("login",__name__, template_folder="templates")


def login_required(f):
    @wraps(f)
    def decorate_fuction(*args, **kwargs):
        if 'user_id' not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorate_fuction

@login_bp.route("/")
def index():
    return render_template("index.html")

@login_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        password = request.form.get('password')

        # Validaciones básicas
        if not nombre or not email or not password:
            return "Todos los campos son obligatorios."

        # if rol not in ['user']:
        #     return "El rol debe ser 'admin' o 'user'.", 400

        password_encriptado = generate_password_hash(password)

        try:
            with sqlite3.connect('biblioteca.db') as conn:
                cursor = conn.cursor()

                cursor.execute('SELECT * FROM usuarios WHERE email = ?', (email,))
                if cursor.fetchone():
                    return "El email ya está registrado. Usa otro email."

                cursor.execute(
                    'INSERT INTO usuarios (nombre, email, password, rol) VALUES (?, ?, ?, "user")',
                    (nombre, email, password_encriptado)
                )
                conn.commit()

            return redirect(url_for('login.login'))
        except sqlite3.Error as e:
            return f"Error en la base de datos: {e}"
    return render_template('register.html')


@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if not email or not password:
            return "El email y la contraseña son obligatorios.", 400

        try:
            with sqlite3.connect('biblioteca.db') as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM usuarios WHERE email = ?', (email,))
                usuario = cursor.fetchone()

                if usuario and check_password_hash(usuario['password'], password):
                    # Guardar los datos en la sesión
                    session['user_id'] = usuario['id_usuario']
                    session['user_name'] = usuario['nombre']
                    session['user_role'] = usuario['rol']

                    # Redirigir según el rol del usuario
                    if usuario['rol'] == 'admin':
                        return redirect(url_for('administrador.admin_index'))
                    else:
                        return redirect(url_for('index.index'))

                return "Credenciales incorrectas.", 401
        except sqlite3.Error as e:
            return f"Error en la base de datos: {e}", 500

    return render_template('login.html')


@login_bp.route('/logout')
def logout():
    # Limpia toda la sesión al cerrar sesión
    session.clear()
    return redirect(url_for('login.login'))

