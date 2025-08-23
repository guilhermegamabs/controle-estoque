from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from werkzeug.security import check_password_hash
from functools import wraps
from dotenv import load_dotenv

import os
import db as database

app = Flask(__name__)
load_dotenv()
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

with app.app_context():
    database.criar_tabelas()

@app.route('/')
@login_required
def dashboard():
    estatisticas = database.obter_estatisticas()
    ultimas_movimentacoes = database.listar_ultimas_movimentacoes()
    return render_template('dashboard.html', stats=estatisticas, ultimas_movimentacoes=ultimas_movimentacoes, active_page='dashboard')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
            email = request.form['email']
            senha = request.form['senha']
            usuario = database.obter_usuario_por_email(email)
            if usuario and check_password_hash(usuario['senha'], senha):
                session.clear()
                session['user_id'] = usuario['id_usuario']
                session['user_name'] = usuario['nome_usuario']
                flash(f"Bem-vindo, {usuario['nome_usuario']}!", 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Email ou senha inválidos.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('login'))
    
@app.route('/equipamentos')
@login_required
def listar_equipamentos():
    lista_de_equipamentos = database.listar_equipamentos()
    return render_template('equipamentos.html', equipamentos=lista_de_equipamentos, active_page='equipamentos')

@app.route('/equipamentos/novo', methods=['GET', 'POST'])
@login_required
def novo_equipamento():
    if request.method == 'POST':
        nome = request.form['nome_equipamento']
        descricao = request.form['descricao_equipamento']
        quantidade = request.form['quantidade_estoque']
        database.adicionar_equipamento(nome, descricao, quantidade)
        flash(f"Equipamento '{nome}' cadastrado com sucesso!", 'success')
        return redirect(url_for('listar_equipamentos'))
    return render_template('adicionar_equipamento.html', active_page='equipamentos')

@app.route('/equipamentos/editar/<int:id_equipamento>', methods=['GET', 'POST'])
@login_required
def editar_equipamento(id_equipamento):
    equipamento = database.obter_equipamento_por_id(id_equipamento)
    if not equipamento:
        flash('Equipamento não encontrado!', 'danger')
        return redirect(url_for('listar_equipamentos'))
    if request.method == 'POST':
        nome = request.form['nome_equipamento']
        descricao = request.form['descricao_equipamento']
        quantidade = request.form['quantidade_estoque']
        database.atualizar_equipamento(id_equipamento, nome, descricao, quantidade)
        flash('Equipamento atualizado com sucesso!', 'success')
        return redirect(url_for('listar_equipamentos'))
    return render_template('editar_equipamento.html', equipamento=equipamento, active_page='equipamentos')

@app.route('/equipamentos/excluir/<int:id_equipamento>', methods=['POST'])
@login_required
def excluir_equipamento_rota(id_equipamento):
    if database.verificar_movimentacoes_abertas_equipamento(id_equipamento):
        flash('Não é possível desativar este equipamento, pois ele possui unidades em reparo.', 'danger')
        return redirect(url_for('listar_equipamentos'))
    
    sucesso = database.desativar_equipamento(id_equipamento)
    if sucesso:
        flash('Equipamento desativado com sucesso! Ele não aparecerá mais nas listas.', 'success')
    else:
        flash('Erro ao desativar o equipamento.', 'danger')
    return redirect(url_for('listar_equipamentos'))

@app.route('/usuarios')
@login_required
def listar_usuarios():
    lista_de_usuarios = database.listar_usuarios()
    return render_template('usuarios.html', usuarios=lista_de_usuarios, active_page='usuarios')

@app.route('/usuarios/novo', methods=['GET', 'POST'])
@login_required
def novo_usuario():
    if request.method == 'POST':
        nome = request.form['nome_usuario']
        email = request.form['email']
        senha = request.form['senha']
        cargo = request.form['cargo']
        nivel_acesso = request.form['nivel_acesso']
        database.adicionar_usuario(nome, email, senha, cargo, nivel_acesso)
        flash(f"Usuário '{nome}' cadastrado com sucesso!", 'success')
        return redirect(url_for('listar_usuarios'))
    return render_template('adicionar_usuario.html', active_page='usuarios')

@app.route('/usuarios/editar/<int:id_usuario>', methods=['GET', 'POST'])
@login_required
def editar_usuario(id_usuario):
    usuario = database.obter_usuario_por_id(id_usuario)
    if not usuario:
        flash('Usuário não encontrado!', 'danger')
        return redirect(url_for('listar_usuarios'))
    if request.method == 'POST':
        nome = request.form['nome_usuario']
        email = request.form['email']
        senha = request.form['senha']
        cargo = request.form['cargo']
        nivel_acesso = request.form['nivel_acesso']
        database.atualizar_usuario(id_usuario, nome, email, senha, cargo, nivel_acesso)
        flash('Usuário atualizado com sucesso!', 'success')
        return redirect(url_for('listar_usuarios'))
    return render_template('editar_usuario.html', usuario=usuario, active_page='usuarios')

@app.route('/usuarios/excluir/<int:id_usuario>', methods=['POST'])
@login_required
def excluir_usuario_rota(id_usuario):
    sucesso = database.excluir_usuario(id_usuario)
    if sucesso:
        flash('Usuário excluído com sucesso!', 'success')
    else:
        flash('Não é possível excluir este usuário, pois ele possui movimentações registradas.', 'danger')
    return redirect(url_for('listar_usuarios'))

@app.route('/movimentacoes')
@login_required
def listar_movimentacoes():
    movimentacoes_abertas = database.listar_movimentacoes_abertas()
    return render_template('movimentacoes.html', movimentacoes=movimentacoes_abertas, active_page='movimentacoes')

@app.route('/movimentacoes/retirada', methods=['GET', 'POST'])
@login_required
def registrar_retirada():
    if request.method == 'POST':
        ids_equipamentos = request.form.getlist('id_equipamentos')
        id_usuario = request.form['id_usuario']
        id_cliente = request.form['id_cliente']
        observacao = request.form['observacao']
        total_registrado = 0
        for id_equipamento in ids_equipamentos:
            quantidade = 1 
            equipamento = database.obter_equipamento_por_id(id_equipamento)
            if equipamento and equipamento['quantidade_estoque'] >= quantidade:
                database.registrar_retirada(id_equipamento, id_usuario, id_cliente, quantidade, observacao)
                total_registrado += 1
            else:
                flash(f"Não foi possível registrar '{equipamento['nome_equipamento']}' por falta de estoque.", 'warning')
        if total_registrado > 0:
            flash(f'{total_registrado} equipamento(s) registrado(s) com sucesso!', 'success')
        return redirect(url_for('listar_movimentacoes'))
    equipamentos = database.listar_equipamentos()
    usuarios = database.listar_usuarios()
    clientes = database.listar_clientes()
    return render_template('registrar_retirada.html', 
                           equipamentos=equipamentos,
                           usuarios=usuarios,
                           clientes=clientes,
                           active_page='movimentacoes')

@app.route('/movimentacoes/devolver/<int:id_movimentacao>', methods=['POST'])
@login_required
def registrar_devolucao_rota(id_movimentacao):
    database.registrar_devolucao(id_movimentacao)
    flash('Devolução registrada com sucesso!', 'success')
    return redirect(url_for('listar_movimentacoes'))

@app.route('/clientes')
@login_required
def listar_clientes():
    lista_de_clientes = database.listar_clientes()
    return render_template('clientes.html', clientes=lista_de_clientes, active_page='clientes')

@app.route('/clientes/novo', methods=['GET', 'POST'])
@login_required
def novo_cliente():
    if request.method == 'POST':
        nome = request.form['nome_cliente']
        contato = request.form['contato']
        database.adicionar_cliente(nome, contato)
        flash(f"Cliente '{nome}' cadastrado com sucesso!", 'success')
        return redirect(url_for('listar_clientes'))
    return render_template('adicionar_cliente.html', active_page='clientes')

@app.route('/clientes/<int:id_cliente>')
@login_required
def cliente_detalhe(id_cliente):
    cliente = database.obter_cliente_por_id(id_cliente)
    movimentacoes = database.listar_movimentacoes_por_cliente(id_cliente)
    return render_template('cliente_detalhe.html', cliente=cliente, movimentacoes=movimentacoes, active_page='clientes')

if __name__ == '__main__': 
    app.run(host="0.0.0.0", port=5000, debug=True)