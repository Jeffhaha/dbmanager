from flask import Flask
from flask_cors import CORS
from flask_session import Session
from config import SECRET_KEY, UPLOAD_FOLDER
from file_blueprint import file_bp
from database_config_blueprint import db_config_bp
#from query_blueprint import query_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

Session(app)
CORS(app, supports_credentials=True)

# 注册蓝图
app.register_blueprint(file_bp)
app.register_blueprint(db_config_bp)
#app.register_blueprint(query_bp)

if __name__ == '__main__':
    app.run(debug=True)