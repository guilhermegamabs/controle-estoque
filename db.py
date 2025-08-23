import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash
from zoneinfo import ZoneInfo

FUSO_HORARIO_SP = ZoneInfo("America/Sao_Paulo")

def obter_hora_atual():
    return datetime.now(FUSO_HORARIO_SP)

def conectar():
    conn = sqlite3.connect("controle.db", detect_types=sqlite3.PARSE_DECLTYPES)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

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
            data_cadastro DATETIME NOT NULL,
            status TEXT NOT NULL DEFAULT 'Ativo'
        )             
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_cliente TEXT NOT NULL,
            contato TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id_movimentacao INTEGER PRIMARY KEY AUTOINCREMENT,
            id_equipamento INTEGER NOT NULL,
            id_usuario INTEGER NOT NULL,
            id_cliente INTEGER NOT NULL,
            data_retirada DATETIME NOT NULL,
            quantidade_retirada INTEGER NOT NULL,
            data_devolucao DATETIME,
            observacao TEXT,
            FOREIGN KEY(id_equipamento) REFERENCES equipamentos(id_equipamento),
            FOREIGN KEY(id_usuario) REFERENCES usuarios(id_usuario),
            FOREIGN KEY(id_cliente) REFERENCES clientes(id_cliente)
        )                      
    ''')
    conn.commit()
    conn.close()

def adicionar_equipamento(nome, descricao, quantidade):
    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        data_atual = obter_hora_atual()
        cursor.execute('''
           INSERT INTO equipamentos (nome_equipamento, descricao_equipamento, quantidade_estoque, data_cadastro) 
           VALUES (?, ?, ?, ?)
        ''', (nome, descricao, quantidade, data_atual))
        conn.commit()
        print("SUCESSO: Commit realizado no banco de dados.") 
    except sqlite3.Error as e:
        print(f"ERRO CRÍTICO NO CADASTRO: {e}")
        raise 
    finally:
        if conn:
            conn.close()

def listar_equipamentos():
    conn = None
    try:
        conn = conectar()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM equipamentos WHERE status = 'Ativo' ORDER BY nome_equipamento")
        
        resultados = cursor.fetchall()
        
        equipamentos_processados = []
        for eq in resultados:
            eq_dict = dict(eq)
            if isinstance(eq_dict.get('data_cadastro'), str):
                eq_dict['data_cadastro'] = datetime.fromisoformat(eq_dict['data_cadastro'])
            equipamentos_processados.append(eq_dict)
            
        return equipamentos_processados

    except sqlite3.Error as e:
        print(f"Erro ao listar equipamentos: {e}")
        return [] 
    finally:
        if conn:
            conn.close()

def obter_equipamento_por_id(id_equipamento):
    conn = None
    try:
        conn = conectar()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM equipamentos WHERE id_equipamento = ?", (id_equipamento,))
        return cursor.fetchone()
    except sqlite3.Error as e:
        print(f"Erro ao obter equipamento: {e}")
        return None
    finally:
        if conn:
            conn.close()

def atualizar_equipamento(id_equipamento, nome, descricao, quantidade):
    conn = None
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

def desativar_equipamento(id_equipamento):
    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("UPDATE equipamentos SET status = 'Inativo' WHERE id_equipamento = ?", (id_equipamento,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erro ao desativar equipamento: {e}")
        return False
    finally:
        if conn:
            conn.close()

def verificar_movimentacoes_abertas_equipamento(id_equipamento):
    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(id_movimentacao) FROM movimentacoes WHERE id_equipamento = ? AND data_devolucao IS NULL", (id_equipamento,))
        count = cursor.fetchone()[0]
        return count > 0
    except sqlite3.Error as e:
        print(f"Erro ao verificar movimentações de equipamento: {e}")
        return True
    finally:
        if conn:
            conn.close()

# --- Funções de Usuários ---

def adicionar_usuario(nome, email, senha, cargo, nivel_acesso):
    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        senha_hash = generate_password_hash(senha)
        cursor.execute('''
            INSERT INTO usuarios (nome_usuario, email, senha, cargo, nivel_acesso)
            VALUES (?, ?, ?, ?, ?)
        ''', (nome, email, senha_hash, cargo, nivel_acesso))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erro ao adicionar usuário: {e}")
    finally:
        if conn:
            conn.close()

def listar_usuarios():
    conn = None
    try:
        conn = conectar()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id_usuario, nome_usuario, email, cargo, nivel_acesso FROM usuarios ORDER BY nome_usuario")
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Erro ao listar usuários: {e}")
        return []
    finally:
        if conn:
            conn.close()  

def obter_usuario_por_id(id_usuario):
    conn = None
    try:
        conn = conectar()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE id_usuario = ?", (id_usuario,))
        return cursor.fetchone()
    except sqlite3.Error as e:
        print(f"Erro ao obter usuário: {e}")
        return None
    finally:
        if conn:
            conn.close()  

def atualizar_usuario(id_usuario, nome, email, senha, cargo, nivel_acesso):
    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        senha_hash = generate_password_hash(senha)
        cursor.execute('''
            UPDATE usuarios
            SET nome_usuario = ?, email = ?, senha = ?, cargo = ?, nivel_acesso = ?
            WHERE id_usuario = ?
        ''', (nome, email, senha_hash, cargo, nivel_acesso, id_usuario))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erro ao atualizar usuário: {e}") 
    finally:
        if conn:
            conn.close()

def excluir_usuario(id_usuario):
    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id_usuario = ?", (id_usuario,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    except sqlite3.Error as e:
        print(f"Erro ao excluir usuário: {e}")
        return False
    finally:
        if conn:
            conn.close()

def obter_usuario_por_email(email):
    conn = None
    try:
        conn = conectar()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        return cursor.fetchone()
    except sqlite3.Error as e:
        print(f"Erro ao obter usuário por email: {e}")
        return None
    finally:
        if conn:
            conn.close()

# --- Funções de Clientes ---

def adicionar_cliente(nome, contato):
    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO clientes (nome_cliente, contato) VALUES (?, ?)
        ''', (nome, contato))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erro ao adicionar cliente: {e}")
    finally:
        if conn:
            conn.close()

def listar_clientes():
    conn = None
    try:
        conn = conectar()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clientes ORDER BY nome_cliente")
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Erro ao listar clientes: {e}")
        return []
    finally:
        if conn:
            conn.close()

def obter_cliente_por_id(id_cliente):
    conn = None
    try:
        conn = conectar()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clientes WHERE id_cliente = ?", (id_cliente,))
        return cursor.fetchone()
    except sqlite3.Error as e:
        print(f"Erro ao obter cliente: {e}")
        return None
    finally:
        if conn:
            conn.close()

# --- Funções de Movimentações ---

def registrar_retirada(id_equipamento, id_usuario, id_cliente, quantidade, observacao):
    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        data_atual = obter_hora_atual()
        cursor.execute('''
            INSERT INTO movimentacoes (id_equipamento, id_usuario, id_cliente, quantidade_retirada, observacao, data_retirada)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (id_equipamento, id_usuario, id_cliente, quantidade, observacao, data_atual))
        cursor.execute('''
            UPDATE equipamentos
            SET quantidade_estoque = quantidade_estoque - ?
            WHERE id_equipamento = ?
        ''', (quantidade, id_equipamento))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Erro ao registrar retirada: {e}")
        if conn:
            conn.rollback() 
    finally:
        if conn:
            conn.close()

def registrar_devolucao(id_movimentacao):
    conn = None
    try:
        conn = conectar()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id_equipamento, quantidade_retirada FROM movimentacoes WHERE id_movimentacao = ?", (id_movimentacao,))
        movimentacao = cursor.fetchone()
        
        if movimentacao:
            id_equipamento = movimentacao['id_equipamento']
            quantidade_devolvida = movimentacao['quantidade_retirada']
            data_atual = obter_hora_atual()
            cursor.execute('''
                UPDATE movimentacoes
                SET data_devolucao = ?
                WHERE id_movimentacao = ?
            ''', (data_atual, id_movimentacao))
            cursor.execute('''
                UPDATE equipamentos
                SET quantidade_estoque = quantidade_estoque + ?
                WHERE id_equipamento = ?
            ''', (quantidade_devolvida, id_equipamento))
            conn.commit()
        else:
            print(f"Movimentação com ID {id_movimentacao} não encontrada.")
    except sqlite3.Error as e:
        print(f"Erro ao registrar devolução: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

def listar_movimentacoes_abertas():
    conn = None
    try:
        conn = conectar()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT
                m.id_movimentacao, m.data_retirada, m.quantidade_retirada,
                e.nome_equipamento, u.nome_usuario, c.nome_cliente
            FROM movimentacoes m
            JOIN equipamentos e ON m.id_equipamento = e.id_equipamento
            JOIN usuarios u ON m.id_usuario = u.id_usuario
            JOIN clientes c ON m.id_cliente = c.id_cliente
            WHERE m.data_devolucao IS NULL
            ORDER BY m.data_retirada DESC
        ''')
        resultados = cursor.fetchall()
        movimentacoes_processadas = []
        for mov in resultados:
            mov_dict = dict(mov)
            if isinstance(mov_dict.get('data_retirada'), str):
                mov_dict['data_retirada'] = datetime.fromisoformat(mov_dict['data_retirada'])
            movimentacoes_processadas.append(mov_dict)
        return movimentacoes_processadas
    except sqlite3.Error as e:
        print(f"Erro ao listar movimentações abertas: {e}")
        return []
    finally:
        if conn:
            conn.close()

def listar_movimentacoes_por_cliente(id_cliente):
    conn = None
    try:
        conn = conectar()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT m.data_retirada, m.data_devolucao, m.quantidade_retirada, m.observacao, e.nome_equipamento
            FROM movimentacoes m
            JOIN equipamentos e ON m.id_equipamento = e.id_equipamento
            WHERE m.id_cliente = ?
            ORDER BY m.data_retirada DESC
        ''', (id_cliente,))
        resultados = cursor.fetchall()
        movimentacoes_processadas = []
        for mov in resultados:
            mov_dict = dict(mov) 
            if isinstance(mov_dict.get('data_retirada'), str):
                mov_dict['data_retirada'] = datetime.fromisoformat(mov_dict['data_retirada'])
            if isinstance(mov_dict.get('data_devolucao'), str):
                mov_dict['data_devolucao'] = datetime.fromisoformat(mov_dict['data_devolucao'])
            movimentacoes_processadas.append(mov_dict)
        return movimentacoes_processadas
    except sqlite3.Error as e:
        print(f"Erro ao listar movimentações por cliente: {e}")
        return []
    finally:
        if conn:
            conn.close()

# --- Funções de Dashboard ---

def obter_estatisticas():
    conn = None
    stats = {
        'total_equipamentos': 0,
        'em_uso': 0,
        'total_usuarios': 0
    }
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(quantidade_estoque) FROM equipamentos WHERE status = 'Ativo'")
        total_estoque = cursor.fetchone()[0] or 0
        cursor.execute("SELECT SUM(quantidade_retirada) FROM movimentacoes WHERE data_devolucao IS NULL")
        total_em_uso = cursor.fetchone()[0] or 0
        stats['total_equipamentos'] = total_estoque + total_em_uso
        stats['em_uso'] = total_em_uso
        cursor.execute("SELECT COUNT(id_usuario) FROM usuarios")
        stats['total_usuarios'] = cursor.fetchone()[0] or 0
        return stats
    except sqlite3.Error as e:
        print(f"Erro ao obter estatísticas: {e}")
        return stats
    finally:
        if conn:
            conn.close()

def listar_ultimas_movimentacoes(limite=5):
    conn = None
    try:
        conn = conectar()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT
                m.data_retirada, m.data_devolucao, e.nome_equipamento,
                u.nome_usuario, c.id_cliente, c.nome_cliente,
                CASE
                    WHEN m.data_devolucao IS NOT NULL THEN 'Devolução'
                    ELSE 'Retirada'
                END as tipo_movimentacao,
                COALESCE(m.data_devolucao, m.data_retirada) as data_ordenacao
            FROM movimentacoes m
            JOIN equipamentos e ON m.id_equipamento = e.id_equipamento
            JOIN usuarios u ON m.id_usuario = u.id_usuario
            JOIN clientes c ON m.id_cliente = c.id_cliente
            ORDER BY data_ordenacao DESC
            LIMIT ?
        ''', (limite,))
        resultados = cursor.fetchall()
        movimentacoes_processadas = []
        for mov in resultados:
            mov_dict = dict(mov)
            if isinstance(mov_dict.get('data_ordenacao'), str):
                mov_dict['data_ordenacao'] = datetime.fromisoformat(mov_dict['data_ordenacao'].split('.')[0])
            movimentacoes_processadas.append(mov_dict)
        return movimentacoes_processadas
    except sqlite3.Error as e:
        print(f"Erro ao listar últimas movimentações: {e}")
        return []
    finally:
        if conn:
            conn.close()