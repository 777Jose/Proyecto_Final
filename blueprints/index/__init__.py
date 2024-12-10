from flask import Blueprint, render_template, send_file
import sqlite3

index_bp = Blueprint("index", __name__, template_folder="templates")

# Función auxiliar para manejar la conexión a la base de datos
def query_db(query, args=(), one=False):
    conn = sqlite3.connect('biblioteca.db')
    cursor = conn.cursor()
    cursor.execute(query, args)
    rv = cursor.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

# Ruta principal para mostrar los libros y categorías (incluye el carrusel)
@index_bp.route("/")
def index():
    # Consulta para obtener los datos de los libros
    libros = query_db("""
        SELECT 
            libros.titulo, 
            autores.nombre || ' ' || autores.apellido AS autor, 
            categorias.nombre AS categoria, 
            libros.descripcion, 
            libros.archivo,  -- Ruta del PDF
            libros.imagen,   -- Ruta de la imagen
            libros.fecha_publicacion 
        FROM libros
        JOIN autores ON libros.id_autor = autores.id_autor
        JOIN categorias ON libros.id_categoria = categorias.id_categoria
    """)

    # Consulta para obtener las categorías (incluye imagen para el carrusel)
    categorias = query_db("""
        SELECT 
            id_categoria, 
            nombre, 
            descripcion 
        FROM categorias
    """)

    # Renderizar la plantilla index.html con los datos de libros y categorías
    return render_template("index.html", libros=libros, categorias=categorias)

# Ruta para mostrar todas las categorías
@index_bp.route("/categorias")
def categorias():
    # Consulta para obtener las categorías
    categorias = query_db("""
        SELECT 
            id_categoria, 
            nombre, 
            descripcion 
        FROM categorias
    """)
    return render_template("cat_libros.html", categorias=categorias)

# Ruta dinámica para mostrar libros por categoría
@index_bp.route("/categoria/<int:categoria_id>")
def libros_por_categoria(categoria_id):
    # Consulta para obtener los libros de una categoría específica
    libros = query_db("""
        SELECT 
            libros.titulo, 
            autores.nombre || ' ' || autores.apellido AS autor, 
            libros.descripcion, 
            libros.archivo,  -- Ruta del PDF
            libros.imagen,   -- Ruta de la imagen
            libros.fecha_publicacion 
        FROM libros
        JOIN autores ON libros.id_autor = autores.id_autor
        WHERE libros.id_categoria = ?
    """, (categoria_id,))
    
    # Consulta para obtener información de la categoría seleccionada
    categoria = query_db("""
        SELECT nombre, descripcion 
        FROM categorias 
        WHERE id_categoria = ?
    """, (categoria_id,), one=True)
    
    return render_template("cat_libros.html", libros=libros, categoria=categoria)

# Ruta para mostrar detalles de un libro específico
@index_bp.route("/libro/<int:libro_id>")
def mostrar_libro(libro_id):
    # Consulta para obtener los datos del libro
    libro = query_db("""
        SELECT 
            libros.titulo, 
            autores.nombre || ' ' || autores.apellido AS autor, 
            libros.descripcion, 
            libros.archivo,  -- Ruta del PDF
            libros.imagen,   -- Ruta de la imagen
            libros.fecha_publicacion
        FROM libros
        JOIN autores ON libros.id_autor = autores.id_autor
        WHERE libros.id_libro = ?
    """, (libro_id,), one=True)
    
    if libro:
        return render_template("libros.html", libro=libro)
    else:
        return "Libro no encontrado", 404
