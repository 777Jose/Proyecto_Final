from flask import Blueprint, render_template, request
import sqlite3

libros_bp = Blueprint("libros", __name__, template_folder="templates")

def query_db(query, args=(), one=False):
    conn = sqlite3.connect('biblioteca.db')
    cursor = conn.cursor()
    cursor.execute(query, args)
    rv = cursor.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

