from portal import database, login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader
def load_usuario(id_usuario):
    return Usuario.query.get(int(id_usuario))

class Usuario(database.Model, UserMixin):
    id = database.Column(database.Integer, primary_key=True)
    nomeGuerra = database.Column(database.String, nullable=False)
    nome = database.Column(database.String, nullable=False)
    graduacao = database.Column(database.String, nullable=False)
    rg = database.Column(database.Integer, unique=True, nullable=False)
    idFuncional = database.Column(database.Integer, unique=True, nullable=False)
    email = database.Column(database.String, nullable=False, unique=True)
    dtNascimento = database.Column(database.DateTime, nullable=False, default=datetime.utcnow)
    tel = database.Column(database.String, nullable=False)
    senha = database.Column(database.String, nullable=False)
    acesso = database.Column(database.String, nullable=False, default='Não informado')
    grupo = database.Column(database.String, nullable=False, default='Não informado')
    unidade = database.Column(database.String, nullable=False, default='Não informado')
    ativo = database.Column(database.String, nullable=False, default='Sim')
    foto_perfil = database.Column(database.String, default='default.png')
    # relacionamento de 1 para muitos com Post, backref='autor' armazena os dados de quem
    # criou o post, dados obtidos pelo lazy, ex: post=Post(), post.autor
    posts = database.relationship('Post', backref='autor', lazy=True)

class Post(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    titulo = database.Column(database.String, nullable=False)
    corpo = database.Column(database.Text, nullable=False)
    dtCriacao = database.Column(database.DateTime, nullable=False, default=datetime.utcnow)
    # relacionamento com Usuario de 1 para 1
    # ATENÇÃO o nome da classe tem que estar em minúsculo na ForeignKey: usuario
    # Nesse caso a ordem dos argumentos importa
    id_usuario = database.Column(database.Integer, database.ForeignKey('usuario.id'), nullable=False)

class Estoque(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    tipo = database.Column(database.String)
    item = database.Column(database.String)
    descricao = database.Column(database.String)
    uni_medida = database.Column(database.String)
    uni_quant = database.Column(database.Integer)
    preco_uni = database.Column(database.Float, default=0.0)
    estoque = database.Column(database.Integer, default=0)

class EstoqueLog(database.Model, UserMixin):
    id = database.Column(database.Integer, primary_key=True)
    rg_responsavel = database.Column(database.Integer, nullable=False)
    acao = database.Column(database.String, nullable=False)
    rg_beneficiario = database.Column(database.Integer)
    item_id = database.Column(database.Integer)
    quantidade = database.Column(database.Integer)
    data = database.Column(database.DateTime, nullable=False, default=datetime.utcnow)

class Atendimento(database.Model, UserMixin):
    id = database.Column(database.Integer, primary_key=True)
    rg_atendente = database.Column(database.Integer, nullable=False)
    qualificacao = database.Column(database.String, nullable=False)
    militar = database.Column(database.String, nullable=False)
    doc_tipo = database.Column(database.String)
    doc_num = database.Column(database.Integer)
    nome = database.Column(database.String)
    assunto = database.Column(database.String, nullable=False)
    solucao = database.Column(database.String)
    dt_ini = database.Column(database.DateTime, nullable=False, default=datetime.now)
    dt_fim = database.Column(database.DateTime)

class Policiais(database.Model, UserMixin):
    id = database.Column(database.Integer, primary_key=True)
    ID_FUNC = database.Column(database.Integer)
    POSTO_GRD = database.Column(database.String)
    NOME_COMPLETO = database.Column(database.String)
    UA = database.Column(database.String)


################### RESET TODAS SENHAS ###########################
'''
from portal.models import Usuario
from portal import bcrypt
lista = []
lista = Usuario.query.filter().all()
for i in lista:
    u = Usuario.query.filter_by(rg=i.rg).first()
    u.senha = bcrypt.generate_password_hash('12345678')
    database.session.add(u)
    database.session.commit()
'''
####################### FIM #################################
