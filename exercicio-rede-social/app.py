# Importando o Flask para a aplicação
from flask import Flask
# Importando o SOCKET IO
from flask_socketio import SocketIO
# Importando o SQLAlchemy
from models.database import db
# Importando os controllers (rotas e chat)
from controllers import routes, chat
import os

# Carregando o Flask na variável "app"
app = Flask(__name__, template_folder='views')

# Configurações do banco (SQLite)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(BASE_DIR, 'models/rede_social.sqlite3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Sessão e uploads
app.config['SECRET_KEY'] = 'chave_secreta_rede_social'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'static/uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

# Configuração do SOCKET IO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# Inicializando o FLASK-SQLALCHEMY
db.init_app(app=app)

# Enviando a variável app para as rotas
routes.init_app(app)
# Iniciando o controller de chat
chat.init_app(socketio)

if __name__ == '__main__':
    # Cria a pasta de uploads caso não exista
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    # Cria as tabelas no banco
    with app.app_context():
        db.create_all()
    # Inicializando o servidor na porta 5000
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
