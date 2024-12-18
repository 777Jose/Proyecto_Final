import os
from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from werkzeug.utils import secure_filename
import sqlite3

UPLOAD_FOLDER_IMG = 'static/img/librosimg/'
UPLOAD_FOLDER_PDF = 'static/img/libros/'

administrador_bp = Blueprint('administrador', __name__, template_folder='templates', static_folder='static')

# Función para ejecutar consultas en la base de datos
def query_db(query, args=(), one=False, commit=False):
    conn = sqlite3.connect('biblioteca.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    try:
        cur.execute(query, args)
        if commit:
            conn.commit()  # Confirma los cambios en la base de datos
        rv = cur.fetchall()
        return (rv[0] if rv else None) if one else rv
    except sqlite3.Error as e:
        print(f"Error en la base de datos: {e}")  # Imprime el error para depuración
        flash(f"Error en la base de datos: {e}", "error")
        return None
    finally:
        conn.close()


@administrador_bp.route('/admin')
def admin_index():
    if session.get('user_role') != 'admin':
        return redirect(url_for('login.login'))

    user_name = session.get('user_name', 'Invitado') 
    return render_template('admin.html', user=user_name)

@administrador_bp.route('/admin/usuarios')
def usuarios():
    if session.get('user_role') != 'admin':
        return redirect(url_for('login.login')) 

    usuarios = query_db("SELECT * FROM usuarios")
    return render_template('usuarios.html', usuarios=usuarios)

@administrador_bp.route('/admin/agregar_usuario', methods=['GET', 'POST'])
def agregar_usuario():
    if session.get('user_role') != 'admin':
        return redirect(url_for('login.login')) 

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
        return redirect(url_for('login.login'))

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

# Mostrar libros
@administrador_bp.route('/libros')
def libros():
    # Verifica si el usuario tiene el rol 'admin'
    if session.get('user_role') != 'admin':
        return redirect(url_for('login.login'))

    # Consulta mejorada para mostrar TODOS los campos de libros, autores y categorías
    libros = query_db("""
        SELECT 
            libros.id_libro, 
            libros.titulo, 
            libros.descripcion, 
            libros.archivo, 
            libros.imagen, 
            libros.fecha_publicacion, 
            libros.fecha_agregado,
            autores.nombre || ' ' || autores.apellido AS autor, 
            categorias.nombre AS categoria
        FROM libros
        JOIN autores ON libros.id_autor = autores.id_autor
        JOIN categorias ON libros.id_categoria = categorias.id_categoria
        ORDER BY libros.fecha_agregado DESC
    """)
    
    # Renderiza la plantilla 'ver_libros.html' pasando los datos de libros
    return render_template('ver_libros.html', libros=libros)

@administrador_bp.route('/admin/editar_libro/<int:id_libro>', methods=['GET', 'POST'])
def editar_libro(id_libro):
    if session.get('user_role') != 'admin':
        return redirect(url_for('login.login'))

    # Obtener datos actuales del libro
    libro = query_db("SELECT * FROM libros WHERE id_libro = ?", (id_libro,), one=True)
    autores = query_db("SELECT id_autor, nombre || ' ' || apellido AS nombre_completo FROM autores")
    categorias = query_db("SELECT id_categoria, nombre FROM categorias")

    if request.method == 'POST':
        titulo = request.form['titulo']
        id_autor = request.form['id_autor']
        id_categoria = request.form['id_categoria']
        descripcion = request.form['descripcion']
        fecha_publicacion = request.form['fecha_publicacion']

        # Manejo de imagen
        if 'imagen' in request.files and request.files['imagen'].filename:
            file_img = request.files['imagen']
            filename_img = secure_filename(file_img.filename)
            file_img.save(os.path.join(UPLOAD_FOLDER_IMG, filename_img))
            imagen = filename_img
        else:
            imagen = libro['imagen']

        # Manejo de archivo PDF
        if 'archivo' in request.files and request.files['archivo'].filename:
            file_pdf = request.files['archivo']
            filename_pdf = secure_filename(file_pdf.filename)
            file_pdf.save(os.path.join(UPLOAD_FOLDER_PDF, filename_pdf))
            archivo = filename_pdf
        else:
            archivo = libro['archivo']

        # Actualizar en la base de datos
        print("Actualizando libro con:", titulo, id_autor, id_categoria, descripcion, imagen, archivo, fecha_publicacion)
        query_db("""
                UPDATE libros 
                SET titulo = ?, id_autor = ?, id_categoria = ?, descripcion = ?, 
                imagen = ?, archivo = ?, fecha_publicacion = ?
                WHERE id_libro = ?
                """, (titulo, id_autor, id_categoria, descripcion, imagen, archivo, fecha_publicacion, id_libro), commit=True)

        flash('Libro actualizado correctamente.', 'success')
        return redirect(url_for('administrador.libros'))

    return render_template('editar_libro.html', libro=libro, autores=autores, categorias=categorias)

@administrador_bp.route('/admin/agregar_libro', methods=['GET', 'POST'])
def agregar_libro():
    if session.get('user_role') != 'admin':
        return redirect(url_for('login.login'))

    autores = query_db("SELECT id_autor, nombre || ' ' || apellido AS nombre_completo FROM autores")
    categorias = query_db("SELECT id_categoria, nombre FROM categorias")

    if request.method == 'POST':
        titulo = request.form['titulo']
        id_autor = request.form['id_autor']
        id_categoria = request.form['id_categoria']
        descripcion = request.form['descripcion']
        fecha_publicacion = request.form['fecha_publicacion']

        # Manejar imagen
        imagen = None
        if 'imagen' in request.files:
            file_img = request.files['imagen']
            if file_img.filename:
                imagen = secure_filename(file_img.filename)
                file_img.save(os.path.join('static/img/librosimg/', imagen))

        # Manejar archivo PDF
        archivo = None
        if 'archivo' in request.files:
            file_pdf = request.files['archivo']
            if file_pdf.filename:
                archivo = secure_filename(file_pdf.filename)
                file_pdf.save(os.path.join('static/img/libros/', archivo))

        # Insertar el libro en la base de datos
        query_db("""
                INSERT INTO libros (titulo, id_autor, id_categoria, descripcion, imagen, archivo, fecha_publicacion)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (titulo, id_autor, id_categoria, descripcion, imagen, archivo, fecha_publicacion), commit=True)

        flash('Libro agregado exitosamente.', 'success')
        return redirect(url_for('administrador.libros'))

    return render_template('agregar_libro.html', autores=autores, categorias=categorias)


# Eliminar un libro
@administrador_bp.route('/admin/eliminar_libro', methods=['GET', 'POST'])
def eliminar_libro():
    if session.get('user_role') != 'admin':
        return redirect(url_for('login.login'))  # Redirige al login si no es admin

    if request.method == 'POST':
        # Obtener el ID del libro a eliminar desde el formulario
        id_libro = request.form.get('id_libro')

        if not id_libro:
            flash('No se seleccionó un libro para eliminar.', 'error')
            return redirect(url_for('administrador.eliminar_libro'))

        try:
            # Eliminar el libro de la base de datos
            query_db("DELETE FROM libros WHERE id_libro = ?", (id_libro,), commit=True)
            flash('Libro eliminado exitosamente.', 'success')
        except sqlite3.Error as e:
            flash(f'Ocurrió un error al eliminar el libro: {e}', 'error')
            print(f"Error SQLite: {e}")

    # Obtener todos los libros para mostrarlos en la tabla
    libros = query_db("""
        SELECT 
            libros.id_libro, 
            libros.titulo, 
            autores.nombre || ' ' || autores.apellido AS autor, 
            categorias.nombre AS categoria
        FROM libros
        JOIN autores ON libros.id_autor = autores.id_autor
        JOIN categorias ON libros.id_categoria = categorias.id_categoria
        ORDER BY libros.id_libro ASC
    """)
    return render_template('eliminar_libro.html', libros=libros)

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
