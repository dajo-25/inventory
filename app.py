from flask import Flask, jsonify, request, render_template, send_from_directory
import sqlite3
import os

app = Flask(__name__, static_folder='static', template_folder='templates')
DB_PATH = os.getenv('DB_PATH', '/app/data/db.sqlite')

# Helper para conexión
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Rutas de API para objetos
@app.route('/api/objects', methods=['GET'])
def list_objects():
    q = request.args.get('q', '')
    db = get_db()
    sql = "SELECT * FROM objects"
    params = ()
    if q:
        sql += " WHERE name LIKE ? OR description LIKE ? OR category LIKE ? OR subcategory LIKE ?"
        term = f"%{q}%"
        params = (term, term, term, term)
    items = db.execute(sql, params).fetchall()
    return jsonify([dict(ix) for ix in items])

@app.route('/api/objects/<int:item_id>', methods=['GET'])
def get_object(item_id):
    db = get_db()
    row = db.execute("SELECT * FROM objects WHERE id = ?", (item_id,)).fetchone()
    return jsonify(dict(row)) if row else ('', 404)

@app.route('/api/objects', methods=['POST'])
def create_object():
    data = request.json
    db = get_db()
    cur = db.execute(
        "INSERT INTO objects (name, description, quantity, category, subcategory, stored_in) VALUES (?,?,?,?,?,?)",
        (data['name'], data['description'], data['quantity'], data['category'], data['subcategory'], data['stored_in'])
    )
    db.commit()
    return jsonify({'id': cur.lastrowid}), 201

@app.route('/api/objects/<int:item_id>', methods=['PUT'])
def update_object(item_id):
    data = request.json
    db = get_db()
    db.execute(
        "UPDATE objects SET name=?, description=?, quantity=?, category=?, subcategory=?, stored_in=? WHERE id=?",
        (data['name'], data['description'], data['quantity'], data['category'], data['subcategory'], data['stored_in'], item_id)
    )
    db.commit()
    return ('', 204)

# Rutas de API para contenedores
@app.route('/api/containers', methods=['GET'])
def list_containers():
    q = request.args.get('q', '')
    db = get_db()
    sql = "SELECT * FROM containers"
    params = ()
    if q:
        sql += " WHERE name LIKE ? OR description LIKE ?"
        term = f"%{q}%"
        params = (term, term)
    rows = db.execute(sql, params).fetchall()
    return jsonify([dict(ix) for ix in rows])

@app.route('/api/containers/<int:cont_id>', methods=['GET'])
def get_container(cont_id):
    db = get_db()
    row = db.execute("SELECT * FROM containers WHERE id = ?", (cont_id,)).fetchone()
    return jsonify(dict(row)) if row else ('', 404)

@app.route('/api/containers', methods=['POST'])
def create_container():
    data = request.json
    db = get_db()
    cur = db.execute(
        "INSERT INTO containers (name, description) VALUES (?,?)",
        (data['name'], data['description'])
    )
    db.commit()
    return jsonify({'id': cur.lastrowid}), 201

@app.route('/api/containers/<int:cont_id>', methods=['PUT'])
def update_container(cont_id):
    data = request.json
    db = get_db()
    db.execute(
        "UPDATE containers SET name=?, description=? WHERE id=?",
        (data['name'], data['description'], cont_id)
    )
    db.commit()
    return ('', 204)

# Rutas para servir front-end
@app.route('/')
def root_redirect():
    return render_template('objects_list.html')

@app.route('/<path:filename>')
def serve_file(filename):
    if filename.startswith('static/'):
        return send_from_directory('.', filename)
    return render_template(filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)