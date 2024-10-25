from flask import Blueprint, jsonify, request, session, g
from sqlalchemy import create_engine, text, inspect
import sqlite3
from config import get_db_path
from database_config_blueprint import decrypt_password

query_bp = Blueprint('query', __name__)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(get_db_path())
    return db

@query_bp.route('/api/database-schema/<int:db_id>', methods=['GET'])
def get_database_schema(db_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM databases WHERE id = ?", (db_id,))
    database = cursor.fetchone()
    
    if not database:
        return jsonify({"error": "Database not found"}), 404

    columns = [column[0] for column in cursor.description]
    db_config = dict(zip(columns, database))
    
    try:
        if db_config['type'] == 'SQLite':
            conn = sqlite3.connect(db_config['database'])
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            schema = {}
            for table in tables:
                table_name = table[0]
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [column[1] for column in cursor.fetchall()]
                schema[table_name] = columns
            conn.close()
        else:
            engine = create_engine(get_connection_string(db_config))
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            schema = {}
            for table in tables:
                columns = [column['name'] for column in inspector.get_columns(table)]
                schema[table] = columns
        return jsonify(schema)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@query_bp.route('/api/execute-query', methods=['POST'])
def execute_query():
    data = request.json
    db_id = data.get('databaseId') or session.get('connected_db')
    query = data.get('query')

    if not db_id or not query:
        return jsonify({"error": "Missing database ID or query"}), 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM databases WHERE id = ?", (db_id,))
    database = cursor.fetchone()
    
    if not database:
        return jsonify({"error": "Database not found"}), 404

    columns = [column[0] for column in cursor.description]
    db_config = dict(zip(columns, database))
    
    try:
        engine = create_engine(get_connection_string(db_config))
        with engine.connect() as connection:
            result = connection.execute(text(query))
            columns = result.keys()
            rows = [dict(row) for row in result.fetchall()]
        return jsonify({"columns": list(columns), "rows": rows})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

def get_connection_string(db):
    if db['type'] == 'MySQL':
        return f"mysql+pymysql://{db['user']}:{decrypt_password(db['password'])}@{db['host']}:{db['port']}/{db['database']}"
    elif db['type'] == 'PostgreSQL':
        return f"postgresql://{db['user']}:{decrypt_password(db['password'])}@{db['host']}:{db['port']}/{db['database']}"
    elif db['type'] == 'SQLite':
        return f"sqlite:///{db['database']}"
    elif db['type'] == 'Oracle':
        return f"oracle+cx_oracle://{db['user']}:{decrypt_password(db['password'])}@{db['host']}:{db['port']}/?service_name={db['database']}"
    elif db['type'] == 'MongoDB':
        return f"mongodb://{db['user']}:{decrypt_password(db['password'])}@{db['host']}:{db['port']}/{db['database']}"
    else:
        raise ValueError(f"Unsupported database type: {db['type']}")

