from flask import Blueprint, render_template, session, redirect, url_for

administrador_bp = Blueprint('administrador', __name__, template_folder='templates', static_folder='static')

@administrador_bp.route('/admin')
def admin_index():
    if session.get('user_role') != 'admin':
        return redirect(url_for('login.login'))  # Redirige al login si no es admin

    user_name = session.get('user_name', 'Invitado')  # Mostrar el nombre del usuario
    return render_template('admin.html', user=user_name)

