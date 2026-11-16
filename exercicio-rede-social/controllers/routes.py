# Importando o Flask para a aplicação
from flask import render_template, request, redirect, url_for, flash, session
# Importando os Models
from models.database import db, Usuario, Post
# Importando a biblioteca Werkzeug
from werkzeug.security import generate_password_hash, check_password_hash
# Importando a biblioteca OS (Manipula o sistema operacional)
import os
# Importando a biblioteca UUID (Gera um nome aleatório para o arquivo)
import uuid

# LISTA DE EXTENSÕES PERMITIDAS
FILE_TYPES = set(['png', 'jpg', 'jpeg', 'gif'])


# FUNÇÃO PARA VALIDAR O TIPO DE ARQUIVO ENVIADO
def arquivos_permitidos(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in FILE_TYPES


# Criando a função principal para inicializar as rotas
def init_app(app):
    # FUNÇÃO DE MIDDLEWARE
    @app.before_request
    def check_auth():
        # Rotas que precisam de autenticação
        rotasProtegidas = ['feed', 'upload', 'chat']
        # Se o usuário estiver tentando acessar uma rota protegida sem estar autenticado
        if request.endpoint in rotasProtegidas and 'user_id' not in session:
            return redirect(url_for('login'))

    # ROTA PRINCIPAL
    @app.route('/')
    def home():
        if 'user_id' in session:
            return redirect(url_for('feed'))
        return redirect(url_for('login'))

    # ROTA DE CADASTRO
    @app.route('/cadastro', methods=['GET', 'POST'])
    def cadastro():
        if request.method == 'POST':
            # COLETA OS DADOS DO FORMULÁRIO
            nome = request.form['nome']
            email = request.form['email']
            senha = request.form['senha']
            # VERIFICANDO SE O E-MAIL JÁ ESTÁ CADASTRADO
            if Usuario.query.filter_by(email=email).first():
                flash('Este e-mail já está cadastrado!', 'danger')
                return redirect(url_for('cadastro'))
            # GERANDO O HASH DE SENHA (CRIPTOGRAFIA)
            senha_com_hash = generate_password_hash(senha, method='scrypt')
            # ENVIANDO OS DADOS PARA O MODEL
            novo_usuario = Usuario(nome=nome, email=email, senha=senha_com_hash)
            # GRAVANDO NO BANCO
            db.session.add(novo_usuario)
            db.session.commit()
            flash('Cadastro realizado com sucesso! Faça seu login.', 'success')
            return redirect(url_for('login'))
        return render_template('cadastro.html')

    # ROTA DE LOGIN
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        # VERIFICANDO SE O MÉTODO É POST
        if request.method == 'POST':
            # COLETANDO OS DADOS DO USUÁRIO
            email = request.form['email']
            senha = request.form['senha']
            # BUSCANDO O USUÁRIO NO BANCO
            usuario = Usuario.query.filter_by(email=email).first()
            # SE O USUARIO EXISTIR E A SENHA (hash) ESTIVER CORRETA
            if usuario and check_password_hash(usuario.senha, senha):
                # AQUI SERÁ CRIADO A SESSÃO
                session['user_id'] = usuario.id
                session['usuario_nome'] = usuario.nome
                session['usuario_email'] = usuario.email
                # Mensagem de Feedback
                flash('Você foi autenticado com sucesso! Bem-vindo!', 'success')
                return redirect(url_for('feed'))
            # CASO USUÁRIO NÃO EXISTA OU SENHA INCORRETA
            flash('Falha no login. Verifique os dados e tente novamente!', 'danger')
            return redirect(url_for('login'))
        return render_template('login.html')

    # ROTA DE LOGOUT
    @app.route('/logout')
    def logout():
        # Destruindo a sessão do usuário
        session.clear()
        return redirect(url_for('login'))

    # ROTA DO FEED
    @app.route('/feed')
    def feed():
        # Selecionando os posts do mais recente para o mais antigo
        posts = Post.query.order_by(Post.data_post.desc()).all()
        return render_template('feed.html', posts=posts)

    # ROTA DE UPLOAD
    @app.route('/upload', methods=['POST'])
    def upload():
        # RECEBENDO O ARQUIVO DO FORMULÁRIO
        file = request.files['file']
        legenda = request.form.get('legenda')
        # Verificar se a extensão é válida
        if not arquivos_permitidos(file.filename):
            flash('Arquivo não permitido! Envie somente imagens (png, jpg, jpeg, gif).', 'danger')
            return redirect(url_for('feed'))
        # Gere um nome aleatório para o arquivo (mantendo a extensão)
        extensao = file.filename.rsplit('.', 1)[1].lower()
        filename = str(uuid.uuid4()) + '.' + extensao
        # Salva o arquivo no servidor (na pasta uploads)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        # Grava o post no banco
        post = Post(imagem=filename, legenda=legenda,
                    usuario_id=session['user_id'])
        db.session.add(post)
        db.session.commit()
        flash('Foto publicada com sucesso!', 'success')
        return redirect(url_for('feed'))

    # ROTA DO CHAT
    @app.route('/chat')
    def chat():
        return render_template('chat.html',
                               nickname=session.get('usuario_nome'))
