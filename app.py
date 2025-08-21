from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from werkzeug.security import check_password_hash
from functools import wraps

import db as database

app = Flask(__name__)
app.config['SECRET_KEY'] = 'uma-chave-secreta-muito-dificil'

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
    return render_template('dashboard.html', stats=estatisticas, ultimas_movimentacoes=ultimas_movimentacoes)

# --- ROTA DE LOGIN
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
    
# --- ROTAS DE EQUIPAMENTOS ---

@app.route('/equipamentos')
@login_required
def listar_equipamentos():
    lista_de_equipamentos = database.listar_equipamentos()
    return render_template('equipamentos.html', equipamentos=lista_de_equipamentos)

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
    
    return render_template('adicionar_equipamento.html')

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

    return render_template('editar_equipamento.html', equipamento=equipamento)

@app.route('/equipamentos/excluir/<int:id_equipamento>', methods=['POST'])
@login_required
def excluir_equipamento_rota(id_equipamento):
    database.excluir_equipamento(id_equipamento)
    flash('Equipamento excluído com sucesso!', 'success')
    return redirect(url_for('listar_equipamentos'))

# --- ROTAS DE USUÁRIOS ---

@app.route('/usuarios')
@login_required
def listar_usuarios():
    lista_de_usuarios = database.listar_usuarios()
    return render_template('usuarios.html', usuarios=lista_de_usuarios)

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
    
    return render_template('adicionar_usuario.html')

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

    return render_template('editar_usuario.html', usuario=usuario)

@app.route('/usuarios/excluir/<int:id_usuario>', methods=['POST'])
@login_required
def excluir_usuario_rota(id_usuario):
    database.excluir_usuario(id_usuario)
    flash('Usuário excluído com sucesso!', 'success')
    return redirect(url_for('listar_usuarios'))

# --- ROTAS DE MOVIMENTAÇÕES ---

@app.route('/movimentacoes')
@login_required
def listar_movimentacoes():
    movimentacoes_abertas = database.listar_movimentacoes_abertas()
    return render_template('movimentacoes.html', movimentacoes=movimentacoes_abertas)

@app.route('/movimentacoes/retirada', methods=['GET', 'POST'])
@login_required
def registrar_retirada():
    if request.method == 'POST':
        id_equipamento = request.form['id_equipamento']
        id_usuario = request.form['id_usuario']
        quantidade = int(request.form['quantidade_retirada'])
        observacao = request.form['observacao']

        equipamento = database.obter_equipamento_por_id(id_equipamento)
        if equipamento and quantidade > equipamento['quantidade_estoque']:
            flash(f"Erro: Quantidade de retirada ({quantidade}) é maior que o estoque disponível ({equipamento['quantidade_estoque']}).", 'danger')
            return redirect(url_for('registrar_retirada'))

        database.registrar_retirada(id_equipamento, id_usuario, quantidade, observacao)
        flash('Retirada registrada com sucesso!', 'success')
        return redirect(url_for('listar_movimentacoes'))

    equipamentos = database.listar_equipamentos()
    usuarios = database.listar_usuarios()
    return render_template('registrar_retirada.html', equipamentos=equipamentos, usuarios=usuarios)

@app.route('/movimentacoes/devolver/<int:id_movimentacao>', methods=['POST'])
@login_required
def registrar_devolucao_rota(id_movimentacao):
    database.registrar_devolucao(id_movimentacao)
    flash('Devolução registrada com sucesso!', 'success')
    return redirect(url_for('listar_movimentacoes'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)