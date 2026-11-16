# Importando o Flask-SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
# Carregando o SQLAlchemy em uma variável
db = SQLAlchemy()


class Usuario(db.Model):
    # Atributos
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)

    # Relacionamento 1 para N com Post
    posts = db.relationship('Post', backref='autor', lazy=True)

    def __init__(self, nome, email, senha):
        self.nome = nome
        self.email = email
        self.senha = senha


class Post(db.Model):
    # Atributos
    id = db.Column(db.Integer, primary_key=True)
    imagem = db.Column(db.String(255), nullable=False)
    legenda = db.Column(db.String(255), nullable=True)
    data_post = db.Column(db.DateTime, default=datetime.now)

    # Chave estrangeira
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'),
                           nullable=False)

    def __init__(self, imagem, legenda, usuario_id):
        self.imagem = imagem
        self.legenda = legenda
        self.usuario_id = usuario_id
