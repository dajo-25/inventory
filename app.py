from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from rapidfuzz import fuzz
import sqlite3, os

app = Flask(__name__, static_folder='static', template_folder='templates')

# 1) CORS: permitir Authorization y métodos OPTIONS
CORS(app, resources={r"/api/*": {
    "origins": "*",
    "allow_headers": ["Authorization", "Content-Type"],
    "methods": ["GET","POST","PUT","DELETE","OPTIONS"]
}})

# 2) Cargar token Bearer
with open('/app/data/bearer.txt') as f:
    app.config['BEARER_TOKEN'] = f.read().strip()

DB_PATH = os.environ.get('DB_PATH', '/app/data/db.sqlite')
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 3) Interceptor que salta OPTIONS
@app.before_request
def require_bearer_auth():
    if request.method == 'OPTIONS':
        return
    if request.path.startswith('/api/'):
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid Authorization header'}), 401
        token = auth.split(' ', 1)[1]
        if token != app.config['BEARER_TOKEN']:
            return jsonify({'error': 'Invalid token'}), 401

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
def list_objects_pyfuzzy():
    app.logger.info("Hdefaef")
    app.logger.warning("Hdefaef")
    app.logger.debug("Hdefaef")
    app.logger.error("Hdefaef")
    q = request.args.get('q', '').strip().lower()
    # 1) primer pas: LIKE simplificat (sense accents, prefiltre)
    cursor.execute("""
      SELECT * FROM objects 
    """)
    candidates = cursor.fetchall()
    if q:
        print("")
    else:
        return jsonify([map_object_row(c) for c in candidates])

    results = []
    for r in candidates:
        words = q.lower().split(" ")
        scores = [];
        mean = 0.0;
            #print(r['name'])
        for w in words:
            score = fuzz.partial_ratio(r['name'].lower(), w)
            #print(f"score for {w} {score}")
            scores.append(score)
            mean += score
        mean = mean / len(scores)
        if mean > 60.0:   # llindar, p.ex. 70%
            results.append((r, mean))
# ordenar per millor puntuació
    results.sort(key=lambda x: x[1], reverse=True)
    return jsonify([map_object_row(r) for r, _ in results])

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
    app.run(host='0.0.0.0', port=8000, debug=True)
