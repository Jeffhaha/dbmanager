from flask import Flask, jsonify, request, session
from flask_cors import CORS
from werkzeug.utils import secure_filename
from sqlalchemy import create_engine, text, inspect
import pymysql
from pymysql.err import OperationalError
import psycopg2
#import pyodbc
import oracledb
#import ibm_db
import pymongo
import logging
from cryptography.fernet import Fernet
import os
from flask_session import Session
import sys
import traceback
import sqlite3
from flask import g
from config import SECRET_KEY,UPLOAD_FOLDER, get_db_path

DATABASE = get_db_path()
# 设置日志记录
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

Session(app)
CORS(app, supports_credentials=True)


# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 密钥管理
def get_or_create_key():
    key_file = 'secret.key'
    if os.path.exists(key_file):
        with open(key_file, 'rb') as file:
            return file.read()
    else:
        key = Fernet.generate_key()
        with open(key_file, 'wb') as file:
            file.write(key)
        return key

#key = get_or_create_key()
key = SECRET_KEY
cipher_suite = Fernet(key)

def encrypt_password(password):
    return cipher_suite.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password):
    return cipher_suite.decrypt(encrypted_password.encode()).decode()

# 模拟数据库存储
databases = [
    {"id": 1, "name": "Local MySQL", "type": "MySQL", "host": "localhost", "port": "3306", "user": "root", "password": "", "database": "test_db", "status": "Disconnected"},
    {"id": 2, "name": "Production PostgreSQL", "type": "PostgreSQL", "host": "prod-server", "port": "5432", "user": "admin", "password": "", "database": "prod_db", "status": "Disconnected"},
    {"id": 3, "name": "MS SQL Server", "type": "MSSQL", "host": "mssql-server", "port": "1433", "user": "sa", "password": "", "database": "msdb", "status": "Disconnected"},
    {"id": 4, "name": "Oracle DB", "type": "Oracle", "host": "oracle-server", "port": "1521", "user": "system", "password": "", "database": "ORCL", "status": "Disconnected"},
    {"id": 5, "name": "IBM DB2", "type": "DB2", "host": "db2-server", "port": "50000", "user": "db2admin", "password": "", "database": "sample", "status": "Disconnected"},
    {"id": 6, "name": "MongoDB", "type": "MongoDB", "host": "mongo-server", "port": "27017", "user": "mongouser", "password": "", "database": "admin", "status": "Disconnected"},
]

# 添加以下函数来获取数据库连接
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# 在 app.teardown_appcontext 中关闭数据库连接
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# 初始化数据库表
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

# 在主函数中调用 init_db()


# 修改 get_databases 函数
@app.route('/api/databases', methods=['GET'])
def get_databases():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM databases")
    databases = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
    for db in databases:
        db['password'] = '********'  # 隐藏密码
    return jsonify(databases)

# 修改 update_database 函数
@app.route('/api/databases/<int:db_id>', methods=['PUT'])
def update_database(db_id):
    data = request.json
    db = get_db()
    cursor = db.cursor()
    
    # 检查数据库是否存在
    cursor.execute("SELECT * FROM databases WHERE id = ?", (db_id,))
    existing_db = cursor.fetchone()
    
    if existing_db:
        # 更新现有数据库
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
        # 插入新数据库
        cursor.execute("""
            INSERT INTO databases (name, type, host, port, user, password, database, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['name'], data['type'], data['host'], data['port'], data['user'],
            encrypt_password(data['password']), data['database'], data['status']
        ))
    
    db.commit()
    return jsonify({"message": "Database updated successfully"})

# 添加新的路由来切换数据库连接状态
@app.route('/api/databases/<int:db_id>/toggle', methods=['POST'])
def toggle_database_connection(db_id):
    db = get_db()
    cursor = db.cursor()
    
    # 获取当前数据库状态
    cursor.execute("SELECT status FROM databases WHERE id = ?", (db_id,))
    current_status = cursor.fetchone()[0]
    
    new_status = 'Connected' if current_status == 'Disconnected' else 'Disconnected'
    
    # 更新数据库状态
    cursor.execute("UPDATE databases SET status = ? WHERE id = ?", (new_status, db_id))
    db.commit()
    
    return jsonify({"message": f"Database {new_status}", "status": new_status})

# 修改 test_database_connection 函数
@app.route('/api/databases/<int:db_id>/test', methods=['POST'])
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

@app.route('/api/database-schema/<int:db_id>', methods=['GET'])
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
            # 对于 SQLite 数据库，我们直接从文件读取 schema
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
            # 对于其他类型的数据库，我们使用 SQLAlchemy
            engine = create_engine(get_connection_string(db_config))
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            schema = {}
            for table in tables:
                columns = [column['name'] for column in inspector.get_columns(table)]
                schema[table] = columns
        return jsonify(schema)
    except Exception as e:
        app.logger.error(f"Error fetching database schema: {str(e)}")
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

@app.route('/api/execute-query', methods=['POST'])
def execute_query():
    data = request.json
    db_id = data.get('databaseId') or session.get('connected_db')
    query = data.get('query')

    if not db_id or not query:
        return jsonify({"error": "Missing database ID or query"}), 400

    #db = next((db for db in databases if db['id'] == db_id), None)
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

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({"message": "File uploaded successfully", "filename": filename})

@app.route('/api/databases/<int:db_id>', methods=['GET'])
def get_database(db_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM databases WHERE id = ?", (db_id,))
    database = cursor.fetchone()
    
    if database:
        columns = [column[0] for column in cursor.description]
        database_dict = dict(zip(columns, database))
        database_dict['password'] = '********'  # 隐藏密码
        return jsonify(database_dict)
    else:
        return jsonify({"error": "Database not found"}), 404

if __name__ == '__main__':
    init_db()
    try:
        app.run(debug=True)
    except Exception as e:
        print("An error occurred:")
        print(e)
        print(traceback.format_exc())
        logger.error(f"Error starting Flask app: {e}")
        logger.error(traceback.format_exc())
