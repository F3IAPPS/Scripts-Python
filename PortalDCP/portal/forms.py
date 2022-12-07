from flask_wtf import FlaskForm
# FileField necessário para selecionar arquivos e FileAllowed é o validador de formato
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, IntegerField, SelectField, EmailField, DateField, SubmitField, BooleanField, FloatField, RadioField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from portal.models import Usuario
from flask_login import current_user


class FormCriarConta(FlaskForm):
    nomeGuerra = StringField('Nome de guerra', validators=[DataRequired()])
    nome = StringField('Nome completo', validators=[DataRequired()])
    rg = IntegerField('RG', validators=[DataRequired()])
    idFuncional = IntegerField('ID Funcional', validators=[DataRequired()])
    email = EmailField('E-mail', validators=[Email()])
    dtNascimento = DateField('Data de nascimento', validators=[DataRequired()])
    tel = StringField('Telefone', validators=[DataRequired()])
    senha = PasswordField('Crie uma senha', validators=[DataRequired(), Length(8, 12)])
    confimacao = PasswordField('Confirme sua senha', validators=[DataRequired(), EqualTo('senha')])
    btCriar = SubmitField('Criar')

    def validate_rg(self, rg):
        usuario = Usuario.query.filter_by(rg=rg.data).first()
        if usuario:
            raise ValidationError('O RG já está sendo usado!')

    def validate_idFuncional(self, idFuncional):
        usuario = Usuario.query.filter_by(idFuncional=idFuncional.data).first()
        if usuario:
            raise ValidationError('O Id Funcional já está sendo usado!')

    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError('O e-mail já está sendo usado!')


class FormNewPass(FlaskForm):
    rg = IntegerField('RG', validators=[DataRequired()])
    senha = PasswordField('Crie uma senha', validators=[DataRequired(), Length(8, 12)])
    confimacao = PasswordField('Confirme sua senha', validators=[DataRequired(), EqualTo('senha')])
    btCriar = SubmitField('Criar')


class FormLogin(FlaskForm):
    rg = IntegerField('RG', validators=[DataRequired()])
    senha = PasswordField('Digite sua senha',
                          validators=[DataRequired(),
                                      Length(min=8,
                                             max=12,
                                             message='A senha de ser entre %(min)d e %(max)d caracteres')])
    btLogar = SubmitField('Logar')
    lembrar = BooleanField('Lembrar dados de acesso')

class FormEstoque(FlaskForm):
    tipo = StringField('TIPO')
    item = StringField('ITEM')
    descricao = StringField('DESCRIÇÃO DO ITEM')
    uni_medida = StringField('UNID. DE MEDIDA')
    uni_quant = IntegerField('QUANTIDADE')
    preco_uni = FloatField('PREÇO UNITÁRIO')
    btAdicionar = SubmitField('Adicionar')

class FormEditarPerfil(FlaskForm):
    nomeGuerra = StringField('Nome de guerra', validators=[DataRequired()])
    email = EmailField('E-mail', validators=[Email()])
    tel = StringField('Telefone', validators=[DataRequired()])
    acesso = SelectField('Acesso', choices=[
        ('ADMINISTRADOR','Administrador'), ('DCP','DCP'), ('CONFERENTE','Conferente')
    ],validators=[DataRequired()])
    unidade = StringField('Unidade', validators=[DataRequired()])
    ativo = RadioField('Funcionário ativo no Portal', choices=[
        ('SIM','SIM'),('NÃO','NÃO')
    ],validators=[DataRequired()])
    foto_perfil = FileField('Foto Perfil(PNG ou JPG)', validators=[FileAllowed(['png', 'jpg'])])

    btEditar = SubmitField('Salvar')

    def validate_email(self, email):
        if current_user.email != email.data:
            usuario = Usuario.query.filter_by(email=email.data).first()
            if usuario:
                raise ValidationError('O e-mail já está sendo usado!')


class FormAtendimentoBusca(FlaskForm):
    id_func = StringField('ID FUNCIONAL')
    btPesquisa = SubmitField('Pesquisar')


class FormAtendimento(FlaskForm):
    id_func = StringField('ID FUNCIONAL')
    qualificacao = StringField('Qualificação')
    militar = StringField('Militar')
    doc_tipo = StringField('Tipo de documento')
    doc_num = IntegerField('Número do documento')
    nome = StringField('Nome')
    assunto = StringField('Assunto')
    btIniciar = SubmitField('Iniciar atendimento')