from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import sqlite3
import os

# Inicialización de Flask y CORS
app = Flask(__name__, static_folder='static', template_folder='templates')
# Permite todas las rutas, métodos y orígenes. En producción puedes restringir origin a tu dominio.
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

DB_PATH = os.environ.get('DB_PATH', '/app/data/db.sqlite')
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Helpers para mapear filas a JSON en español
def map_object_row(r):
    return {
        'id': r['id'],
        'nombre': r['name'],
        'descripcion': r['description'],
        'cantidad': r['quantity'],
        'categoria': r['category'],
        'subcategoria': r['subcategory'],
        'almacenado_en': r['stored_in']
    }

def map_container_row(r):
    return {
        'id': r['id'],
        'nombre': r['name'],
        'descripcion': r['description']
    }

# ----------------------------
# API Objetos
# ----------------------------
@app.route('/api/objects', methods=['GET'])
def list_objects():
    q = request.args.get('q', '')
    if q:
        cursor.execute("SELECT * FROM objects WHERE name LIKE ?", ('%' + q + '%',))
    else:
        cursor.execute("SELECT * FROM objects")
    rows = cursor.fetchall()
    return jsonify([map_object_row(r) for r in rows])

@app.route('/api/objects/<int:obj_id>', methods=['GET'])
def get_object(obj_id):
    cursor.execute("SELECT * FROM objects WHERE id = ?", (obj_id,))
    r = cursor.fetchone()
    return (jsonify(map_object_row(r)) if r else ('', 404))

@app.route('/api/objects', methods=['POST'])
def add_object():
    data = request.json
    cursor.execute(
        "INSERT INTO objects(name, description, quantity, category, subcategory, stored_in) VALUES (?, ?, ?, ?, ?, ?)",
        (data['nombre'], data['descripcion'], data['cantidad'],
         data['categoria'], data['subcategoria'], data['almacenado_en'])
    )
    conn.commit()
    return jsonify({'id': cursor.lastrowid}), 201

@app.route('/api/objects/<int:obj_id>', methods=['PUT'])
def update_object(obj_id):
    data = request.json
    cursor.execute(
        "UPDATE objects SET name=?, description=?, quantity=?, category=?, subcategory=?, stored_in=? WHERE id=?",
        (data['nombre'], data['descripcion'], data['cantidad'],
         data['categoria'], data['subcategoria'], data['almacenado_en'], obj_id)
    )
    conn.commit()
    return ('', 204)

@app.route('/api/objects/<int:obj_id>', methods=['DELETE'])
def delete_object(obj_id):
    cursor.execute("DELETE FROM objects WHERE id=?", (obj_id,))
    conn.commit()
    return ('', 204)


# ----------------------------
# API Contenedores
# ----------------------------
@app.route('/api/containers', methods=['GET'])
def list_containers():
    q = request.args.get('q', '')
    if q:
        cursor.execute("SELECT * FROM containers WHERE name LIKE ?", ('%' + q + '%',))
    else:
        cursor.execute("SELECT * FROM containers")
    rows = cursor.fetchall()
    return jsonify([map_container_row(r) for r in rows])

@app.route('/api/containers/<int:cont_id>', methods=['GET'])
def get_container(cont_id):
    cursor.execute("SELECT * FROM containers WHERE id = ?", (cont_id,))
    r = cursor.fetchone()
    return (jsonify(map_container_row(r)) if r else ('', 404))

@app.route('/api/containers', methods=['POST'])
def add_container():
    data = request.json
    cursor.execute(
        "INSERT INTO containers(name, description) VALUES (?, ?)",
        (data['nombre'], data['descripcion'])
    )
    conn.commit()
    return jsonify({'id': cursor.lastrowid}), 201

@app.route('/api/containers/<int:cont_id>', methods=['PUT'])
def update_container(cont_id):
    data = request.json
    cursor.execute(
        "UPDATE containers SET name=?, description=? WHERE id=?",
        (data['nombre'], data['descripcion'], cont_id)
    )
    conn.commit()
    return ('', 204)

@app.route('/api/containers/<int:cont_id>', methods=['DELETE'])
def delete_container(cont_id):
    cursor.execute("DELETE FROM containers WHERE id=?", (cont_id,))
    conn.commit()
    return ('', 204)


# ----------------------------
# Ruta front-end
# ----------------------------
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


if __name__ == '__main__':
    # En desarrollo, debug activa recarga y mensajes de error explícitos
    app.run(host='0.0.0.0', port=8000, debug=True)
