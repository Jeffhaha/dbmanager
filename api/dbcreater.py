import sqlite3
from cryptography.fernet import Fernet
import os
import sys
import json
from config import SECRET_KEY, CFGDB
    
# 添加父目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
db_dir = os.path.join(parent_dir, 'db')
os.makedirs(db_dir, exist_ok=True)
sqlite_db = os.path.join(db_dir, CFGDB)


# 使用 SECRET_KEY 创建 Fernet 实例
cipher_suite = Fernet(SECRET_KEY.encode())

def encrypt_password(password):
    return cipher_suite.encrypt(password.encode()).decode()

def decrypt_password(encrypted_password):
    return cipher_suite.decrypt(encrypted_password.encode()).decode()

def create_db():
    conn = sqlite3.connect(sqlite_db)
    cursor = conn.cursor()
    
    # 从 schema.sql 文件读取并执行 SQL 语句
    schema_path = os.path.join(current_dir, 'schema.sql')
    with open(schema_path, 'r') as schema_file:
        schema_sql = schema_file.read()
        cursor.executescript(schema_sql)
    
    conn.commit()
    conn.close()

    print(f"Database '{sqlite_db}' created successfully.")

def add_database(name, db_type, host, port, user, password, database, status="Disconnected"):
    conn = sqlite3.connect(sqlite_db)
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO databases (name, type, host, port, user, password, database, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, db_type, host, port, user, encrypt_password(password), database, status))
    
    conn.commit()
    conn.close()
    print(f"Database '{name}' added successfully.")

def update_database(id, name, db_type, host, port, user, password, database, status):
    conn = sqlite3.connect(sqlite_db)
    cursor = conn.cursor()
    
    cursor.execute('''
    UPDATE databases
    SET name = ?, type = ?, host = ?, port = ?, user = ?, password = ?, database = ?, status = ?
    WHERE id = ?
    ''', (name, db_type, host, port, user, encrypt_password(password), database, status, id))
    
    conn.commit()
    conn.close()
    print(f"Database with ID {id} updated successfully.")

def delete_database(id):
    conn = sqlite3.connect(sqlite_db)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM databases WHERE id = ?', (id,))
    
    conn.commit()
    conn.close()
    print(f"Database with ID {id} deleted successfully.")

def list_databases():
    conn = sqlite3.connect(sqlite_db)
    conn.row_factory = sqlite3.Row  # 这允许我们通过列名访问数据
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM databases')
    databases = cursor.fetchall()
    
    conn.close()
    
    # 将查询结果转换为字典列表
    result = []
    for db in databases:
        db_dict = dict(db)
        # 解密密码
        #db_dict['password'] = decrypt_password(db_dict['password'])
        result.append(db_dict)
    
    # 返回 JSON 格式的数据
    return json.dumps(result, indent=2)

if __name__ == '__main__':
    #create_db()
    
    # 示例用法
    #add_database("Local MySQL", "MySQL", "localhost", "3306", "root", "password", "test_db")
    #add_database("Production PostgreSQL", "PostgreSQL", "prod-server", "5432", "admin", "secure_password", "prod_db")
    
    # 获取并打印数据库列表
    #databases_json = list_databases()
    #print(databases_json)
    
    #update_database(1, "Updated MySQL", "MySQL", "localhost", "3306", "root", "new_password", "new_db", "Connected")
    
    # 再次获取并打印更新后的数据库列表
    #databases_json = list_databases()
    #print(databases_json)
    
    #delete_database(2)
    
    # 最后一次获取并打印数据库列表
    databases_json = list_databases()
    print(databases_json)
