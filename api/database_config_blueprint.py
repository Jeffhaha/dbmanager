from flask import Blueprint, jsonify, request, g
from config import get_db_path, SECRET_KEY
from cryptography.fernet import Fernet
import sqlite3
import logging
from sqlalchemy import create_engine, text, inspect


db_config_bp = Blueprint('db_config', __name__)

# 设置日志记录
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 使用 SECRET_KEY 创建 Fernet 实例
cipher_suite = Fernet(SECRET_KEY.encode())

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(get_db_path())
    return db

@db_config_bp.teardown_app_request
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def encrypt_password(password):
    return cipher_suite.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password):
    return cipher_suite.decrypt(encrypted_password.encode()).decode()

@db_config_bp.route('/api/databases', methods=['GET'])
def get_databases():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM databases")
    databases = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    #for db in databases:
        #db['password'] = '********'  # 隐藏密码
    return jsonify(databases)

@db_config_bp.route('/api/databases/<int:db_id>', methods=['GET', 'PUT'])
def manage_database(db_id):
    if request.method == 'GET':
        return get_database(db_id)
    elif request.method == 'PUT':
        return update_database(db_id)

def get_database(db_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM databases WHERE id = ?", (db_id,))
    database = cursor.fetchone()
    
    if database:
        columns = [column[0] for column in cursor.description]
        database_dict = dict(zip(columns, database))
        #database_dict['password'] = '********'  # 隐藏密码
        return jsonify(database_dict)
    else:
        return jsonify({"error": "Database not found"}), 404

def update_database(db_id):
    data = request.json
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("SELECT * FROM databases WHERE id = ?", (db_id,))
    existing_db = cursor.fetchone()
    
    if existing_db:
        cursor.execute("""
            UPDATE databases 
            SET name = ?, type = ?, host = ?, port = ?, user = ?, password = ?, database = ?, status = ?
            WHERE id = ?
        """, (
            data['name'], data['type'], data['host'], data['port'], data['user'],
            encrypt_password(data['password']) if data['password'] else existing_db[6],
            data['database'], data['status'], db_id
        ))
    else:
        cursor.execute("""
            INSERT INTO databases (name, type, host, port, user, password, database, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['name'], data['type'], data['host'], data['port'], data['user'],
            encrypt_password(data['password']), data['database'], data['status']
        ))
    
    db.commit()
    return jsonify({"message": "Database updated successfully"})

@db_config_bp.route('/api/databases/<int:db_id>/toggle', methods=['POST'])
def toggle_database_connection(db_id):
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("SELECT status FROM databases WHERE id = ?", (db_id,))
    current_status = cursor.fetchone()[0]
    
    new_status = 'Connected' if current_status == 'Disconnected' else 'Disconnected'
    
    cursor.execute("UPDATE databases SET status = ? WHERE id = ?", (new_status, db_id))
    db.commit()
    
    return jsonify({"message": f"Database {new_status}", "status": new_status})

@db_config_bp.route('/api/databases/<int:db_id>/test', methods=['POST'])
def test_database_connection(db_id):
    data = request.json
    logger.debug(f"Received connection test request for database ID: {db_id}")
    logger.debug(f"Connection details: {data}")

    try:
        logger.debug(f"Attempting to connect to database: {data['name']} (Type: {data['type']})")
        
        if data['type'] == 'MySQL':
            connection = pymysql.connect(
                host=data['host'],
                user=data['user'],
                password=data['password'],
                database=data['database'],
                port=int(data['port'])
            )
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            connection.close()
        elif data['type'] == 'PostgreSQL':
            connection = psycopg2.connect(
                host=data['host'],
                user=data['user'],
                password=data['password'],
                dbname=data['database'],
                port=int(data['port'])
            )
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            connection.close()
        #elif data['type'] == 'MSSQL':
        #    connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={data['host']},{data['port']};DATABASE={data['database']};UID={data['user']};PWD={data['password']}"
        #    connection = pyodbc.connect(connection_string)
        #    with connection.cursor() as cursor:
        #        cursor.execute("SELECT 1")
        #    connection.close()
        elif data['type'] == 'Oracle':
            connection = oracledb.connect(
                user=data['user'],
                password=data['password'],
                dsn=f"{data['host']}:{data['port']}/{data['database']}"
            )
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 FROM DUAL")
            connection.close()
        #elif data['type'] == 'DB2':
        #    connection_string = f"DATABASE={data['database']};HOSTNAME={data['host']};PORT={data['port']};PROTOCOL=TCPIP;UID={data['user']};PWD={data['password']}"
        #    connection = ibm_db.connect(connection_string, "", "")
        #    ibm_db.close(connection)
        elif data['type'] == 'MongoDB':
            client = pymongo.MongoClient(f"mongodb://{data['user']}:{data['password']}@{data['host']}:{data['port']}/{data['database']}")
            client.server_info()
            client.close()
        else:
            raise ValueError(f"Unsupported database type: {data['type']}")
        
        logger.info(f"Successfully connected to {data['type']} database: {data['name']}")
        
        # 更新数据库状态
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE databases SET status = 'Connected' WHERE id = ?", (db_id,))
        db.commit()
        
        return jsonify({"message": "Connection test successful", "status": "Connected"})
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error when connecting to {data['name']}: {error_message}")
        return jsonify({"error": f"Connection test failed: {error_message}"}), 400


@db_config_bp.route('/api/database-schema/<int:db_id>', methods=['GET'])
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

@db_config_bp.route('/api/execute-query', methods=['POST'])
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

