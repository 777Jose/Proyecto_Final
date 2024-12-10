from flask import Blueprint, render_template, session, redirect, url_for, flash, request
import sqlite3

administrador_bp = Blueprint('administrador', __name__, template_folder='templates', static_folder='static')

# Función para ejecutar consultas en la base de datos
def query_db(query, args=(), one=False):
    conn = sqlite3.connect('biblioteca.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.commit()
    conn.close()
    return (rv[0] if rv else None) if one else rv

@administrador_bp.route('/admin')
def admin_index():
    if session.get('user_role') != 'admin':
        return redirect(url_for('login.login'))  # Redirige al login si no es admin

    user_name = session.get('user_name', 'Invitado')  # Mostrar el nombre del usuario
    return render_template('admin.html', user=user_name)



@administrador_bp.route('/admin/usuarios')
def usuarios():
    if session.get('user_role') != 'admin':
        return redirect(url_for('login.login'))  # Redirige al login si no es admin

    usuarios = query_db("SELECT * FROM usuarios")
    return render_template('usuarios.html', usuarios=usuarios)

@administrador_bp.route('/admin/agregar_usuario', methods=['GET', 'POST'])
def agregar_usuario():
    if session.get('user_role') != 'admin':
        return redirect(url_for('login.login'))  # Redirige al login si no es admin

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        password = request.form.get('password')
        rol = request.form.get('rol')

        if not nombre or not email or not password or not rol:
            flash('Por favor, completa todos los campos.', 'error')
            return render_template('agregar_user.html')

        try:
            query_db("""
                INSERT INTO usuarios (nombre, email, password, rol)
                VALUES (?, ?, ?, ?)
            """, (nombre, email, password, rol))
            flash('Usuario agregado exitosamente.', 'success')
            return redirect(url_for('administrador.usuarios'))
        except sqlite3.IntegrityError:
            flash('El email ya está registrado. Intenta con otro.', 'error')

    return render_template('agregar_user.html')

@administrador_bp.route('/admin/editar_usuario/<int:id_usuario>', methods=['GET', 'POST'])
def editar_usuario(id_usuario):
    if session.get('user_role') != 'admin':
        return redirect(url_for('login.login'))  # Redirige al login si no es admin

    if request.method == 'POST':
        # Obtener los datos del formulario
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        rol = request.form.get('rol')

        # Validar que los campos no estén vacíos
        if not nombre or not email or not rol:
            flash('Por favor, completa todos los campos.', 'error')
            return redirect(url_for('administrador.editar_usuario', id_usuario=id_usuario))

        try:
            # Actualizar los datos del usuario en la base de datos
            query_db("""
                UPDATE usuarios
                SET nombre = ?, email = ?, rol = ?
                WHERE id_usuario = ?
            """, (nombre, email, rol, id_usuario))
            flash('Usuario actualizado exitosamente.', 'success')
            return redirect(url_for('administrador.usuarios'))
        except sqlite3.IntegrityError:
            flash('El correo ingresado ya está en uso. Intenta con otro.', 'error')
            return redirect(url_for('administrador.editar_usuario', id_usuario=id_usuario))

    # Obtener los datos del usuario actual para mostrar en el formulario
    usuario = query_db("SELECT * FROM usuarios WHERE id_usuario = ?", (id_usuario,), one=True)
    if not usuario:
        flash('Usuario no encontrado.', 'error')
        return redirect(url_for('administrador.usuarios'))

    return render_template('editar_user.html', usuario=usuario)


@administrador_bp.route('/admin/eliminar_usuario', methods=['GET', 'POST'])
def eliminar_usuario():
    if session.get('user_role') != 'admin':
        return redirect(url_for('login.login'))  # Redirige al login si no es admin

    if request.method == 'POST':
        # Obtener el ID del usuario a eliminar desde el formulario
        id_usuario = request.form.get('id_usuario')

        if not id_usuario:
            flash('No se seleccionó un usuario para eliminar.', 'error')
            return redirect(url_for('administrador.eliminar_usuario'))

        try:
            # Eliminar el usuario de la base de datos
            query_db("DELETE FROM usuarios WHERE id_usuario = ?", (id_usuario,))
            flash('Usuario eliminado exitosamente.', 'success')
        except sqlite3.Error as e:
            flash(f'Ocurrió un error al eliminar el usuario: {e}', 'error')

    # Obtener todos los usuarios para mostrarlos en la tabla
    usuarios = query_db("SELECT * FROM usuarios")
    return render_template('eliminar_user.html', usuarios=usuarios)



@administrador_bp.route('/admin/libros')
def libros():
    if session.get('user_role') != 'admin':
        return redirect(url_for('login.login'))  # Redirige al login si no es admin

    libros = query_db("""
        SELECT 
            libros.id_libro, 
            libros.titulo, 
            autores.nombre || ' ' || autores.apellido AS autor, 
            categorias.nombre AS categoria, 
            libros.descripcion, 
            libros.fecha_publicacion 
        FROM libros
        JOIN autores ON libros.id_autor = autores.id_autor
        JOIN categorias ON libros.id_categoria = categorias.id_categoria
    """)

    print(libros)  # Para depurar y verificar que los datos se obtienen correctamente
    return render_template('libros.html', libros=libros)


@administrador_bp.route('/admin/nuevo_libro')
def nuevo_libro():
    if session.get('user_role') != 'admin':
        return redirect(url_for('login.login'))  # Redirige al login si no es admin

    return render_template('nuevo_libro.html')

@administrador_bp.route('/admin/eliminar_libro')
def eliminar_libro():
    if session.get('user_role') != 'admin':
        return redirect(url_for('login.login'))  # Redirige al login si no es admin

    return render_template('eliminar_libro.html')

@administrador_bp.route('/admin/categorias', methods=['GET'])
def categorias():
    if session.get('user_role') != 'admin':
        return redirect(url_for('login.login'))  # Redirige al login si no es admin

    categorias = query_db("SELECT * FROM categorias")
    return render_template('categorias.html', categorias=categorias)

@administrador_bp.route('/admin/nueva_categoria', methods=['GET', 'POST'])
def nueva_categoria():
    if session.get('user_role') != 'admin':
        return redirect(url_for('login.login'))  # Redirige al login si no es admin

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')

        if not nombre or not descripcion:
            flash('Por favor, completa todos los campos.', 'error')
            return redirect(url_for('administrador.nueva_categoria'))

        try:
            query_db("""
                INSERT INTO categorias (nombre, descripcion)
                VALUES (?, ?)
            """, (nombre, descripcion))
            flash('Categoría creada exitosamente.', 'success')
            return redirect(url_for('administrador.categorias'))
        except sqlite3.IntegrityError:
            flash('El nombre de la categoría ya existe. Intenta con otro.', 'error')

    return render_template('agregar_cat.html')


@administrador_bp.route('/admin/editar_categoria/<int:id_categoria>', methods=['GET', 'POST'])
def editar_categoria(id_categoria):
    if session.get('user_role') != 'admin':
        return redirect(url_for('login.login'))  # Redirige al login si no es admin

    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')

        if not nombre or not descripcion:
            flash('Por favor, completa todos los campos.', 'error')
            return redirect(url_for('administrador.editar_categoria', id_categoria=id_categoria))

        try:
            query_db("""
                UPDATE categorias
                SET nombre = ?, descripcion = ?
                WHERE id_categoria = ?
            """, (nombre, descripcion, id_categoria))
            flash('Categoría actualizada exitosamente.', 'success')
            return redirect(url_for('administrador.categorias'))
        except sqlite3.IntegrityError:
            flash('El nombre de la categoría ya existe. Intenta con otro.', 'error')

    categoria = query_db("SELECT * FROM categorias WHERE id_categoria = ?", (id_categoria,), one=True)
    if not categoria:
        flash('Categoría no encontrada.', 'error')
        return redirect(url_for('administrador.categorias'))

    return render_template('editar_cat.html', categoria=categoria)

@administrador_bp.route('/admin/eliminar_categoria/<int:id_categoria>', methods=['POST'])
def eliminar_categoria(id_categoria):
    if session.get('user_role') != 'admin':
        return redirect(url_for('login.login'))  # Redirige al login si no es admin

    try:
        query_db("DELETE FROM categorias WHERE id_categoria = ?", (id_categoria,))
        flash('Categoría eliminada exitosamente.', 'success')
    except sqlite3.Error as e:
        flash(f'Ocurrió un error al eliminar la categoría: {e}', 'error')

    return redirect(url_for('administrador.categorias'))
