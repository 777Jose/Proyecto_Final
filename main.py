from flask import Flask
import sqlite3
from blueprints.login import login_bp
from blueprints.index import index_bp
from blueprints.administrador import administrador_bp

app = Flask(__name__)
app.secret_key = 'miclavesecreta'

def init_db():
    conn = sqlite3.connect('biblioteca.db')
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS usuarios (
        id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        rol TEXT CHECK(rol IN ('admin', 'user')) NOT NULL,
        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS autores (
        id_autor INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        apellido TEXT NOT NULL,
        biografia TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS categorias (
        id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT UNIQUE NOT NULL,
        descripcion TEXT
        )
        """
    )
        
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS libros (
        id_libro INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        id_autor INTEGER NOT NULL,
        id_categoria INTEGER NOT NULL,
        descripcion TEXT,
        archivo TEXT NOT NULL,
        imagen TEXT,
        fecha_publicacion DATE,
        fecha_agregado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_autor) REFERENCES Autores(id_autor),
        FOREIGN KEY (id_categoria) REFERENCES Categorias(id_categoria)
        )
        """
    )
        
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS historial (
        id_historial INTEGER PRIMARY KEY AUTOINCREMENT,
        id_usuario INTEGER NOT NULL,
        id_libro INTEGER NOT NULL,
        fecha_descarga TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario),
        FOREIGN KEY (id_libro) REFERENCES Libros(id_libro)
        )

        
        """
    )
    conn.commit()
    conn.close()

init_db()

app.register_blueprint(index_bp)
app.register_blueprint(login_bp)
app.register_blueprint(administrador_bp)

if __name__ == "__main__":
    app.run(debug=True)