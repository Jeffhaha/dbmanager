
@app.route('/api/databases/<int:db_id>', methods=['PUT'])
def update_database(db_id):
    db = next((db for db in databases if db['id'] == db_id), None)
    if db:
        data = request.json
        allowed_fields = ['name', 'host', 'port', 'user', 'database', 'password']
        for field in allowed_fields:
            if field in data:
                if field == 'password':
                    db[field] = data[field]  # Store password as plain text for now
                else:
                    db[field] = data[field]
        db_type = db['type'].lower().replace(" ", "")
        DATABASES[db_type].update({k: v for k, v in data.items() if k in allowed_fields})
        save_config(DATABASES)
        return jsonify({k: v for k, v in db.items() if k not in ['password']})
    return jsonify({"error": "Database not found"}), 404

@app.route('/api/databases/<int:db_id>/test', methods=['POST'])
def test_database_connection(db_id):
    db = next((db for db in databases if db['id'] == db_id), None)
    if db:
        try:
            logger.debug(f"Attempting to connect to database: {db['name']} (Type: {db['type']})")
            logger.debug(f"Connection details: Host: {db['host']}, Port: {db['port']}, User: {db['user']}, Database: {db['database']}")
            if db['type'] == 'MySQL':
                # 直接使用pymysql进行连接测试
                connection = pymysql.connect(
                    host=db['host'],
                    user=db['user'],
                    password=db['password'],
                    database=db['database'],
                    port=int(db['port'])
                )
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                connection.close()
            else:
                connection_string = get_connection_string(db)
                engine = create_engine(connection_string)
                with engine.connect() as connection:
                    result = connection.execute(text("SELECT 1"))
                    result.fetchone()
            db['status'] = 'Connected'
            return jsonify({"message": "Connection test successful"})
        except OperationalError as e:
            db['status'] = 'Disconnected'
            error_message = str(e)
            logger.error(f"OperationalError when connecting to {db['name']}: {error_message}")
            if "Access denied" in error_message:
                error_message += " Please check your username and password."
            return jsonify({"error": f"Connection test failed: {error_message}"}), 400
        except Exception as e:
            db['status'] = 'Disconnected'
            return jsonify({"error": f"Connection test failed: {str(e)}"}), 400
    return jsonify({"error": "Database not found"}), 404


@app.route('/api/databases/<int:db_id>', methods=['GET'])
def get_database(db_id):
    db = next((db for db in databases if db['id'] == db_id), None)
    if db:
        safe_db = {k: v for k, v in db.items() if k not in ['password']}
        return jsonify(safe_db)
    return jsonify({"error": "Database not found"}), 404
