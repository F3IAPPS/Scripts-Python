from flask import render_template, redirect, url_for, flash, request
from portal import app, database, bcrypt
from portal.forms import FormLogin, FormCriarConta, FormEditarPerfil
from portal.forms import FormAtendimento, FormAtendimentoBusca, FormEstoque, FormNewPass
from portal.models import Usuario, Atendimento, Post, Estoque, EstoqueLog, Policiais
from flask_login import login_user, logout_user, current_user, login_required
import secrets
import os
from PIL import Image
from datetime import datetime

################# LISTAS GERAIS ###########################
graduacao = ['SD', 'CB', '3º SGT', '2º SGT', '1º SGT',
             'SUBTEN', 'ASP', '2º TEN', '1º TEN',
             'CAP', 'MAJ', 'TENCEL', 'CEL']
################# FIM ###########################

@app.route('/')
def home():
    return render_template('home.html', graduacao=graduacao)


@app.route('/sobre')
@login_required
def sobre():
    return render_template('sobre.html')


@app.route('/usuarios/dcp')
@login_required
def dcp():
    usuarios = Usuario.query.order_by(Usuario.graduacao, Usuario.rg)
    return render_template('usuarios_dcp.html', usuarios=usuarios)


@app.route('/usuarios/conferente')
@login_required
def conferente():
    usuarios = Usuario.query.order_by(Usuario.rg)
    return render_template('usuarios_conferente.html', usuarios=usuarios)


@app.route('/conta/login', methods=['GET', 'POST'])
def logar():
    form = FormLogin()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(rg=form.rg.data).first()

        if usuario:
            check_senha = bcrypt.check_password_hash(usuario.senha, form.senha.data)
            if check_senha:
                login_user(usuario, remember=form.lembrar.data)
                flash(f'Bem vindo {usuario.nomeGuerra}', 'alert-success')
                return redirect(url_for('home'))
            else:
                flash('Lamento! RG ou Senha incorretos', 'alert-danger')
                return redirect(url_for('logar'))

        else:
            flash('Lamento! RG ou Senha incorretos', 'alert-danger')
            return redirect(url_for('logar'))

    return render_template('conta_logar.html', form=form)


@app.route('/conta/criar', methods=['GET', 'POST'])
def criarConta():
    form = FormCriarConta()
    if form.validate_on_submit():
        #criptografia da senha
        senha_crypt = bcrypt.generate_password_hash(form.senha.data)
        # os nomes vêm do models
        usuario = Usuario(nomeGuerra=form.nomeGuerra.data,
                          nome=form.nome.data,
                          rg=form.rg.data,
                          idFuncional=form.idFuncional.data,
                          graduacao=request.form.get('select_grad'),
                          email=form.email.data,
                          dtNascimento=form.dtNascimento.data,
                          tel=form.tel.data,
                          senha=senha_crypt)
        database.session.add(usuario)
        database.session.commit()

        flash('Conta criada com sucesso', 'alert-success')
        return redirect(url_for('logar'))

    return render_template('conta_criar.html', form=form, graduacao=graduacao)


@app.route('/conta/newpass', methods=['GET', 'POST'])
def senha():
    form = FormNewPass()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(rg=form.rg.data).first()
        #criptografia da senha
        senha_crypt = bcrypt.generate_password_hash(form.senha.data)
        usuario.senha = senha_crypt
        database.session.add(usuario)
        database.session.commit()

        flash('Senha alterada', 'alert-success')
        return redirect(url_for('logar'))

    return render_template('conta_newpass.html', form=form)


@app.route('/atendimento/civil', methods=['GET', 'POST'])
@login_required
def atd_civil():
    form = FormAtendimento()
    lista_civil = ['Pensionista', 'Advogado', 'Oficial de justiça', 'Representante Legal', 'Cotista', 'Procurador']
    lista_doc = ['RG', 'CPF', 'OAB', 'CNH']
    lista_assunto = ['Contracheque', 'Consignado', 'Informe de rendimentos', 'E-mail', 'Informação',
                     'Conferência', 'Folha de pagamento', 'Auxílio fardamento', 'Férias', 'Gratificação',
                     'Pensão', 'Abono permanência', 'Fundo de saúde', 'Ajuda de custo', 'Reunião',
                     'Reintegração / Reinclusão', 'Triênio', 'IHP', 'Promoção']
    lista_assunto.sort()

    if form.validate_on_submit():
        a = Atendimento(
            rg_atendente = current_user.rg,
            qualificacao = request.form.get('select_qualificacao'),
            militar = 'Não',
            doc_tipo = request.form.get('select_doc'),
            doc_num = form.doc_num.data,
            nome = form.nome.data,
            assunto = request.form.get('select_assunto'))

        database.session.add(a)
        database.session.commit()

        flash('Atendimento iniciado com sucesso', 'alert-success')
        return redirect(url_for('atd_civil'))

    return render_template('atendimento_civil.html',
                           form=form,
                           lista_civil=lista_civil,
                           lista_doc=lista_doc,
                           lista_assunto=lista_assunto)


policial = ''
def busca(id):
    global policial
    policial = Policiais.query.filter_by(ID_FUNC=id).first()
    return policial

@app.route('/atendimento/busca', methods=['GET', 'POST'])
@login_required
def busca_militar():
    form = FormAtendimentoBusca()

    if form.validate_on_submit():
        id_func = form.id_func.data
        busca(id_func)
        if policial:
            return redirect(url_for('atd_militar'))
        else:
            flash('Lamento Id. Funcional não encontrado', 'alert-danger')

    return render_template('atendimento_militar_busca.html', form=form)


@app.route('/atendimento/militar', methods=['GET', 'POST'])
@login_required
def atd_militar():
    form=FormAtendimento()
    lista_militar = ['Conferente', 'Pensionista', 'Representante Legal', 'Militar']
    lista_assunto = ['Contracheque', 'Consignado', 'Informe de rendimentos', 'E-mail', 'Informação',
                 'Conferência', 'Folha de pagamento', 'Auxílio fardamento', 'Férias', 'Gratificação',
                 'Pensão', 'Abono permanência', 'Fundo de saúde', 'Ajuda de custo', 'Reunião',
                 'Reintegração / Reinclusão', 'Triênio', 'IHP', 'Promoção']
    lista_assunto.sort()

    grad = policial.POSTO_GRD.replace('o', 'º')
    if form.validate_on_submit():
        a = Atendimento(
            rg_atendente=current_user.rg,
            qualificacao=request.form.get('select_qualificacao'),
            militar='Sim',
            doc_tipo='ID FUNCIONAL',
            doc_num=policial.ID_FUNC,
            nome=policial.NOME_COMPLETO,
            assunto=request.form.get('select_assunto'))

        database.session.add(a)
        database.session.commit()

        flash('Atendimento iniciado com sucesso', 'alert-success')
        return redirect(url_for('busca_militar'))

    return render_template('atendimento_militar.html', form=form, lista_militar=lista_militar,
                           lista_assunto=lista_assunto, graduacao=graduacao, policial=policial)


@app.route('/atendimento/lista', methods=['GET', 'POST'])
@login_required
def atd_encerrar():
    lista = Atendimento.query.filter().order_by(Atendimento.dt_ini).all()
    form = FormAtendimento()

    if form.validate_on_submit():
        global id_atendimento
        id_atendimento = request.form.get('id_atendimento')
        return redirect(url_for('atd_solucao'))

    return render_template('atendimento_encerramento.html', form=form, lista=lista)


@app.route('/atendimento/soluccao', methods=['GET', 'POST'])
@login_required
def atd_solucao():
    form = FormAtendimento()
    atd = Atendimento.query.filter_by(id=id_atendimento).first()
    if form.validate_on_submit():
        atd.solucao = request.form.get('solucao')
        atd.dt_fim = datetime.now()
        database.session.add(atd)
        database.session.commit()
        flash('Encerramento concluido com sucesso', 'alert-success')
        return redirect(url_for('atd_encerrar'))

    return render_template('atendimento_solucao.html',form=form,atd=atd)


@app.route('/atendimento/encerrados', methods=['GET', 'POST'])
@login_required
def atd_encerrados():
    atd = Atendimento.query.filter().all()
    form=FormAtendimento()
    return render_template('atendimento_l_encerrados.html', form=form, atd=atd)


@app.route('/sair')
def sair():
    logout_user()
    flash('Você está deslogado!', 'alert-info')
    return redirect(url_for('logar'))


@app.route('/conta/perfil')
@login_required
def perfil():
    foto_perfil = url_for('static', filename=f'fotos/{current_user.foto_perfil}')
    grupo = current_user.grupo.split(',')
    return render_template('perfil.html', foto_perfil=foto_perfil, grupo=grupo)


def savar_imagem(imagem):
    codigo = secrets.token_hex(8)
    nome, extensao = os.path.splitext(imagem.filename)
    nome_arquivo = nome + codigo + extensao
    caminho = os.path.join(app.root_path, 'static/fotos', nome_arquivo)
    tamanho = (512, 512)
    imagem_reduzida = Image.open(imagem)
    imagem_reduzida.thumbnail(tamanho)
    imagem_reduzida.save(caminho)
    #instalar o Pillow caso não esteja instalado
    return nome_arquivo


@app.route('/conta/perfil/editar', methods=['GET', 'POST'])
@login_required
def perfil_editar():
    foto_perfil = url_for('static', filename=f'fotos/{current_user.foto_perfil}')
    form = FormEditarPerfil()

    if form.validate_on_submit():
        current_user.graduacao = request.form.get('select_grad')
        current_user.nomeGuerra = form.nomeGuerra.data
        current_user.email = form.email.data
        current_user.tel = form.tel.data
        current_user.unidade = form.unidade.data
        current_user.acesso = form.acesso.data
        current_user.ativo = form.ativo.data
        lista_grupo = request.form.getlist('checkGrupo')
        opcoes = ''

        for i in lista_grupo:
            opcoes += i+","

        current_user.grupo = opcoes

        if form.foto_perfil.data:
            nome_imagem = savar_imagem(form.foto_perfil.data)
            current_user.foto_perfil = nome_imagem

        database.session.commit()

        flash('Perfil atualizado com sucesso', 'alert-success')
        return redirect(url_for('perfil'))
    elif request.method == 'GET':
        form.nomeGuerra.data = current_user.nomeGuerra
        form.email.data = current_user.email
        form.tel.data = current_user.tel
        form.unidade.data = current_user.unidade
        form.acesso.data = current_user.acesso
        form.ativo.data = current_user.ativo

    return render_template('perfil_editar.html', foto_perfil=foto_perfil, form=form, graduacao=graduacao)


@app.route('/post/criar')
@login_required
def criarPost():
    return render_template('post_criar.html')


@app.route('/post/geral')
@login_required
def exibirPost():
    return render_template('post_geral.html')


@app.route('/estoque/novo', methods=['GET', 'POST'])
@login_required
def estoque_novo():
    form = FormEstoque()
    if form.validate_on_submit():
        item = Estoque(
            tipo=request.form.get('select_tipo'),
            item=form.item.data,
            descricao=form.descricao.data,
            uni_medida=request.form.get('select_uni_medida'),
            uni_quant=form.uni_quant.data)

        database.session.add(item)
        database.session.commit()

        log = EstoqueLog(
            rg_responsavel=current_user.rg,
            acao='Novo item',
            item_id=item.id)

        database.session.add(log)
        database.session.commit()

        flash('Item adicionado a lista com sucesso!', 'alert-success')
        return redirect(url_for('estoque_novo'))

    return render_template('estoque_novo.html', form=form)


@app.route('/estoque/entrada', methods=['GET', 'POST'])
@login_required
def estoque_entrada():
    lista = Estoque.query.filter().order_by(Estoque.item).all()
    form = FormEstoque()

    if form.validate_on_submit():
        itemId = request.form.get('id')
        item = Estoque.query.filter_by(id=itemId).first()
        quantidade = int(request.form.get('quantidade'))
        item.estoque += quantidade
        preco = request.form.get('preco')
        if ',' in preco:
            preco = float(preco.replace(',', '.'))
        else:
            preco = float(preco)

        item.preco_uni = preco

        log = EstoqueLog(
            rg_responsavel=current_user.rg,
            acao='Entrada',
            item_id=item.id,
            quantidade=quantidade)

        database.session.add(item)
        database.session.add(log)
        database.session.commit()
        flash(f'Adicionado: {quantidade} unidades de {item.item}, {item.descricao}, preço unitário R$ {preco}', 'alert-success')
        return redirect(url_for('estoque_entrada'))

    return render_template('estoque_entrada.html', form=form, lista=lista)


@app.route('/estoque/saida', methods=['GET', 'POST'])
@login_required
def estoque_saida():
    lista = Estoque.query.filter().order_by(Estoque.item).all()
    form = FormEstoque()

    if form.validate_on_submit():
        itemId = request.form.get('id')
        item = Estoque.query.filter_by(id=itemId).first()
        quantidade = int(request.form.get('quantidade'))
        item.estoque -= quantidade

        log = EstoqueLog(
            rg_responsavel=current_user.rg,
            acao='Saída',
            item_id=item.id,
            quantidade=quantidade,
            rg_beneficiario=request.form.get('recebedor'))

        database.session.add(item)
        database.session.add(log)
        database.session.commit()
        flash(f'Removido: {quantidade} unidades de {item.item}, {item.descricao}', 'alert-success')
        return redirect(url_for('estoque_saida'))

    return render_template('estoque_saida.html', form=form, lista=lista)


@app.route('/estoque/l_completa')
@login_required
def l_completa():
    lista = Estoque.query.filter().order_by(Estoque.item).all()
    tamanho = len(lista)

    return render_template('estoque_l_completa.html', lista=lista, tamanho=tamanho)


@app.route('/estoque/l_escritorio')
@login_required
def l_escritorio():
    lista = Estoque.query.filter_by(tipo="Escritório").order_by(Estoque.item).all()
    tamanho = len(lista)

    return render_template('estoque_l_escritorio.html', lista=lista, tamanho=tamanho)


@app.route('/estoque/l_limpeza')
@login_required
def l_limpeza():
    lista = Estoque.query.filter_by(tipo="Hig. e Limp.").order_by(Estoque.item).all()
    tamanho = len(lista)

    return render_template('estoque_l_limpeza.html', lista=lista, tamanho=tamanho)


@app.route('/estoque/l_cozinha')
@login_required
def l_cozinha():
    lista = Estoque.query.filter_by(tipo="Alim. e Coz.").order_by(Estoque.item).all()
    tamanho = len(lista)

    return render_template('estoque_l_cozinha.html', lista=lista, tamanho=tamanho)


@app.route('/estoque/l_compras')
@login_required
def l_compras():
    lista = Estoque.query.filter().order_by(Estoque.item).all()
    tamanho = len(lista)

    return render_template('estoque_l_compras.html', lista=lista, tamanho=tamanho)