import sqlite3
from datetime import datetime

def conectar():
    return sqlite3.connect("controle.db")

def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_usuario TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            cargo TEXT,
            nivel_acesso TEXT NOT NULL CHECK (nivel_acesso IN ('Administrador', 'Técnico'))
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS equipamentos (
            id_equipamento INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_equipamento TEXT NOT NULL,
            descricao_equipamento TEXT,
            quantidade_estoque INTEGER NOT NULL DEFAULT 0,
            data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
        )             
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id_movimentacao INTEGER PRIMARY KEY AUTOINCREMENT,
            id_equipamento INTEGER NOT NULL,
            id_usuario INTEGER NOT NULL,
            data_retirada DATETIME DEFAULT CURRENT_TIMESTAMP,
            quantidade_retirada INTEGER NOT NULL,
            data_devolucao DATETIME,
            observacao TEXT,

            FOREIGN KEY(id_equipamento) REFERENCES equipamentos(id_equipamento),
            FOREIGN KEY(id_usuario) REFERENCES usuarios(id_usuario)
        )                      
    ''')
    
    conn.commit()
    conn.close()

def adicionar_equipamento(nome, descricao, quantidade):
    try:
        conn = conectar()
        cursor = conn.cursor()
        
        cursor.execute('''
           INSERT INTO equipamentos (nome_equipamento, descricao_equipamento, quantidade_estoque) VALUES (?, ?, ?)            
        ''', (nome, descricao, quantidade))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erro ao adicionar equipamento: {e}")
    finally:
        if conn:
            conn.close()
            
def listar_equipamentos():
    conn = None
    try:
        conn = conectar()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM equipamentos ORDER BY nome_equipamento")
        res = cursor.fetchall()
        return res
    except sqlite3.Error as e:
        print(f"Erro ao listar equipamentos: {e}")
        return [] 
    finally:
        if conn:
            conn.close()
            
def excluir_equipamento(id_equipamento):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM equipamentos WHERE id_equipamento = ?", (id_equipamento,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erro ao excluir equipamento: {e}")
    finally:
        if conn:
            conn.close()

def listar_um_equipamento(id_equipamento):
    try:
        conn = conectar()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM equipamentos WHERE id_equipamento = ?", (id_equipamento,))
        equipamento = cursor.fetchone()
        return equipamento
    except sqlite3.Error as e:
        print(f"Erro ao obter equipamento: {e}")
        return None
    finally:
        if conn:
            conn.close()
        
def atualizar_equipamento(id_equipamento, nome, descricao, quantidade):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE equipamentos
            SET nome_equipamento = ?, descricao_equipamento = ?, quantidade_estoque = ?
            WHERE id_equipamento = ?
        ''', (nome, descricao, quantidade, id_equipamento))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erro ao atualizar equipamento: {e}")
    finally:
        if conn:
            conn.close()