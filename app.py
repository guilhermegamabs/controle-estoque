from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import db as database

app = Flask(__name__)
app.config['SECRET_KEY'] = 'uma-chave-secreta-muito-dificil'

with app.app_context():
    database.criar_tabelas()

@app.route('/')
def hello():
    return "<h1>Hello World!</h1>"

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

@app.route('/equipamentos')
def listar_equipamentos():
    listar_de_equipamentos = database.listar_equipamentos()
    
    return render_template('equipamentos.html', equipamentos = listar_de_equipamentos)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)

