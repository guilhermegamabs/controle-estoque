from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import db as database

app = Flask(__name__)
app.config['SECRET_KEY'] = 'uma-chave-secreta-muito-dificil'

with app.app_context():
    database.criar_tabelas()

@app.route('/')
def hello():
    return redirect(url_for('listar_equipamentos'))

# --- ROTAS DE EQUIPAMENTOS ---

@app.route('/equipamentos')
def listar_equipamentos():
    lista_de_equipamentos = database.listar_equipamentos()
    return render_template('equipamentos.html', equipamentos=lista_de_equipamentos)

@app.route('/equipamentos/novo', methods=['GET', 'POST'])
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
def excluir_equipamento_rota(id_equipamento):
    database.excluir_equipamento(id_equipamento)
    flash('Equipamento excluído com sucesso!', 'success')
    return redirect(url_for('listar_equipamentos'))

# --- ROTAS DE USUÁRIOS ---

@app.route('/usuarios')
def listar_usuarios():
    lista_de_usuarios = database.listar_usuarios()
    return render_template('usuarios.html', usuarios=lista_de_usuarios)

@app.route('/usuarios/novo', methods=['GET', 'POST'])
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
def excluir_usuario_rota(id_usuario):
    database.excluir_usuario(id_usuario)
    flash('Usuário excluído com sucesso!', 'success')
    return redirect(url_for('listar_usuarios'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)