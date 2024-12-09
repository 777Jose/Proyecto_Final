from flask import Blueprint, render_template
import sqlite3

index_bp = Blueprint("index", __name__, template_folder="templates")

# Ruta principal para mostrar los libros
@index_bp.route("/")
def index():
    # Conexión a la base de datos
    conn = sqlite3.connect('biblioteca.db')
    cursor = conn.cursor()
    
    # Consulta para obtener los datos de los libros incluyendo la nueva columna 'imagen'
    cursor.execute("""
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
    libros = cursor.fetchall()  # Obtener todos los registros
    
    conn.close()  # Cerrar la conexión a la base de datos
    
    # Renderizar la plantilla index.html con los datos de los libros
    return render_template("index.html", libros=libros)

# Nueva ruta para mostrar las categorías
@index_bp.route("/categorias")
def categorias():
    # Conexión a la base de datos
    conn = sqlite3.connect('biblioteca.db')
    cursor = conn.cursor()
    
    # Consulta para obtener las categorías
    cursor.execute("""
        SELECT 
            id_categoria, 
            nombre, 
            descripcion 
        FROM categorias
    """)
    categorias = cursor.fetchall()  # Obtener todos los registros
    
    conn.close()  # Cerrar la conexión a la base de datos
    
    # Renderizar la plantilla categorias.html con los datos de las categorías
    return render_template("categorias.html", categorias=categorias)