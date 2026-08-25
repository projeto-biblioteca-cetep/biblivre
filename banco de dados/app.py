from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# Caminho absoluto para garantir que o banco seja salvo no mesmo diretório deste script
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'biblivre.db')

def get_conexao():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- CRIAÇÃO AUTOMÁTICA DAS TABELAS ---
def inicializar_banco():
    with get_conexao() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cadastro TEXT UNIQUE NOT NULL,
                email TEXT NOT NULL,
                senha TEXT NOT NULL,
                matricula TEXT,
                data_nascimento TEXT,
                ano TEXT,
                turma TEXT,
                curso TEXT,
                tipo TEXT DEFAULT 'aluno',
                cpf TEXT,
                telefone TEXT,
                endereco TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS livros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                autor TEXT NOT NULL,
                genero TEXT,
                capa TEXT,
                icone TEXT DEFAULT '📖',
                formato TEXT,
                local TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emprestimos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_aluno INTEGER NOT NULL,
                id_livro INTEGER NOT NULL,
                data_devolucao TEXT NOT NULL,
                devolvido INTEGER DEFAULT 0,
                FOREIGN KEY (id_aluno) REFERENCES usuarios (id),
                FOREIGN KEY (id_livro) REFERENCES livros (id)
            )
        """)

        # Migração: garante a coluna "devolvido" em bancos criados pela versão antiga
        try:
            cursor.execute("ALTER TABLE emprestimos ADD COLUMN devolvido INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass  # coluna já existe

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mural_mensagens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario INTEGER NOT NULL,
                nome_usuario TEXT NOT NULL,
                conteudo TEXT NOT NULL,
                data_envio DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_usuario) REFERENCES usuarios (id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bug_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario INTEGER,
                nome_usuario TEXT,
                categoria TEXT NOT NULL,
                descricao TEXT NOT NULL,
                data_envio DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'Pendente'
            )
        """)

        # Usuários padrão
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE cadastro = 'GIP-DGB'")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO usuarios (nome, cadastro, email, senha, tipo)
                VALUES ('Desenvolvedor GIP', 'GIP-DGB', 'dev@biblivre.com', 'Ciganoindiano', 'dev')
            """)

        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE cadastro = 'admin'")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO usuarios (nome, cadastro, email, senha, tipo)
                VALUES ('Administrador', 'admin', 'admin@biblivre.com', '123456', 'admin')
            """)

        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE cadastro = 'aluno'")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO usuarios (nome, cadastro, email, senha, tipo, data_nascimento, ano, turma, curso)
                VALUES ('Aluno Exemplo', 'aluno', 'aluno@biblivre.com', '01012005', 'aluno', '2005-01-01', '1º Ano', 'Turma A', 'Informática')
            """)

        conn.commit()

inicializar_banco()


def formatar_senha_por_nascimento(nascimento):
    """Converte uma data 'AAAA-MM-DD' (vinda do <input type=date>) em senha padrão DDMMAAAA."""
    if not nascimento:
        return None
    try:
        ano, mes, dia = nascimento.split('-')
        return f"{dia}{mes}{ano}"
    except Exception:
        return None


# --- ROTA DE LOGIN ---
@app.route('/api/login', methods=['POST'])
def login():
    dados = request.get_json() or {}
    cadastro = dados.get('cadastro')
    senha = dados.get('senha')

    with get_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE cadastro = ? AND senha = ?", (cadastro, senha))
        user = cursor.fetchone()

        if user:
            user_dict = dict(user)
            user_dict.pop('senha', None)
            # alias para o front, que usa "nascimento" e não "data_nascimento"
            user_dict['nascimento'] = user_dict.get('data_nascimento')
            return jsonify({
                "status": "sucesso",
                "mensagem": "Login realizado com sucesso!",
                "usuario": user_dict
            }), 200
        else:
            return jsonify({"status": "erro", "mensagem": "Credenciais inválidas!"}), 401

# --- USUÁRIOS (CRUD) ---
@app.route('/api/usuarios', methods=['GET'])
def listar_usuarios():
    try:
        with get_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, nome, cadastro, email, tipo, matricula,
                       data_nascimento AS nascimento, ano, turma, curso,
                       cpf, telefone, endereco
                FROM usuarios
            """)
            return jsonify([dict(row) for row in cursor.fetchall()]), 200
    except Exception as e:
        return jsonify([]), 200

@app.route('/api/usuarios/<int:id_user>', methods=['GET'])
def obter_usuario(id_user):
    """Necessário para a troca de senha do administrador no painel Dev."""
    with get_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE id = ?", (id_user,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"status": "erro", "mensagem": "Usuário não encontrado."}), 404
        user = dict(row)
        user['nascimento'] = user.get('data_nascimento')
        return jsonify(user), 200

@app.route('/api/usuarios', methods=['POST'])
def criar_usuario():
    dados = request.get_json() or {}
    tipo = dados.get('tipo', 'aluno')
    nascimento = dados.get('nascimento') or dados.get('data_nascimento')
    senha = dados.get('senha')

    # Se não veio senha explícita (caso comum de cadastro de aluno),
    # usa a data de nascimento em formato DDMMAAAA como senha padrão.
    if not senha:
        senha = formatar_senha_por_nascimento(nascimento)

    if not dados.get('nome') or not dados.get('cadastro') or not senha:
        return jsonify({
            "status": "erro",
            "mensagem": "Nome, login e uma senha (ou data de nascimento válida) são obrigatórios."
        }), 400

    try:
        with get_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO usuarios (nome, cadastro, email, senha, matricula, data_nascimento, ano, turma, curso, cpf, telefone, endereco, tipo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                dados.get('nome'), dados.get('cadastro'), dados.get('email'),
                senha, dados.get('matricula'), nascimento,
                dados.get('ano'), dados.get('turma'), dados.get('curso'),
                dados.get('cpf'), dados.get('telefone'), dados.get('endereco'),
                tipo
            ))
            conn.commit()
        return jsonify({"status": "sucesso", "mensagem": "Usuário registrado com sucesso!"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"status": "erro", "mensagem": "Usuário/Login já cadastrado!"}), 400
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route('/api/usuarios/<int:id_user>', methods=['PUT'])
def editar_usuario(id_user):
    dados = request.get_json() or {}
    nascimento = dados.get('nascimento') or dados.get('data_nascimento')
    nova_senha = dados.get('senha')

    try:
        with get_conexao() as conn:
            cursor = conn.cursor()
            if nova_senha:
                cursor.execute("""
                    UPDATE usuarios
                    SET nome=?, cadastro=?, email=?, tipo=?, matricula=?, data_nascimento=?,
                        ano=?, turma=?, curso=?, cpf=?, telefone=?, endereco=?, senha=?
                    WHERE id=?
                """, (
                    dados.get('nome'), dados.get('cadastro'), dados.get('email'), dados.get('tipo'),
                    dados.get('matricula'), nascimento, dados.get('ano'),
                    dados.get('turma'), dados.get('curso'), dados.get('cpf'),
                    dados.get('telefone'), dados.get('endereco'), nova_senha, id_user
                ))
            else:
                cursor.execute("""
                    UPDATE usuarios
                    SET nome=?, cadastro=?, email=?, tipo=?, matricula=?, data_nascimento=?,
                        ano=?, turma=?, curso=?, cpf=?, telefone=?, endereco=?
                    WHERE id=?
                """, (
                    dados.get('nome'), dados.get('cadastro'), dados.get('email'), dados.get('tipo'),
                    dados.get('matricula'), nascimento, dados.get('ano'),
                    dados.get('turma'), dados.get('curso'), dados.get('cpf'),
                    dados.get('telefone'), dados.get('endereco'), id_user
                ))
            conn.commit()
        return jsonify({"status": "sucesso", "mensagem": "Usuário atualizado com sucesso!"}), 200
    except sqlite3.IntegrityError:
        return jsonify({"status": "erro", "mensagem": "O login digitado já pertence a outro usuário."}), 400
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route('/api/usuarios/<int:id_user>', methods=['DELETE'])
def deletar_usuario(id_user):
    try:
        with get_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM usuarios WHERE id=?", (id_user,))
            conn.commit()
        return jsonify({"status": "sucesso", "mensagem": "Usuário removido com sucesso!"}), 200
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

# --- LIVROS (CRUD) ---
@app.route('/api/livros', methods=['GET'])
def listar_livros():
    with get_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM livros")
        return jsonify([dict(row) for row in cursor.fetchall()]), 200

@app.route('/api/livros', methods=['POST'])
def criar_livro():
    dados = request.get_json() or {}
    with get_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO livros (titulo, autor, genero, capa, icone, formato, local)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            dados.get('titulo'), dados.get('autor'), dados.get('genero'),
            dados.get('capa'), dados.get('icone', '📖'), dados.get('formato'), dados.get('local')
        ))
        conn.commit()
    return jsonify({"status": "sucesso", "mensagem": "Livro adicionado!"}), 201

@app.route('/api/livros/<int:id_livro>', methods=['PUT'])
def editar_livro(id_livro):
    dados = request.get_json() or {}
    with get_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE livros
            SET titulo=?, autor=?, genero=?, capa=?, formato=?, local=?
            WHERE id=?
        """, (
            dados.get('titulo'), dados.get('autor'), dados.get('genero'),
            dados.get('capa'), dados.get('formato'), dados.get('local'), id_livro
        ))
        conn.commit()
    return jsonify({"status": "sucesso", "mensagem": "Livro atualizado!"}), 200

@app.route('/api/livros/<int:id_livro>', methods=['DELETE'])
def deletar_livro(id_livro):
    with get_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM livros WHERE id=?", (id_livro,))
        conn.commit()
    return jsonify({"status": "sucesso", "mensagem": "Livro removido!"}), 200

# --- EMPRÉSTIMOS ---
@app.route('/api/emprestimos', methods=['GET'])
def listar_emprestimos():
    with get_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                e.id AS id,
                e.id_aluno AS id_usuario,
                e.id_livro AS id_livro,
                e.data_devolucao AS data_devolucao,
                e.devolvido AS devolvido,
                u.nome AS nome_aluno,
                (COALESCE(u.curso, '') || ' - ' || COALESCE(u.ano, '') || ' ' || COALESCE(u.turma, '')) AS turma_ano,
                l.titulo AS titulo_livro,
                l.icone AS icone
            FROM emprestimos e
            JOIN usuarios u ON e.id_aluno = u.id
            JOIN livros l ON e.id_livro = l.id
            ORDER BY e.id DESC
        """)
        return jsonify([dict(row) for row in cursor.fetchall()]), 200

@app.route('/api/emprestimos', methods=['POST'])
def registrar_emprestimo():
    dados = request.get_json() or {}
    # o front envia "id_usuario"; aceitamos também "id_aluno" por compatibilidade
    id_usuario = dados.get('id_usuario') or dados.get('id_aluno')
    id_livro = dados.get('id_livro')
    data_devolucao = dados.get('data_devolucao')

    if not id_usuario or not id_livro or not data_devolucao:
        return jsonify({
            "status": "erro",
            "mensagem": "Selecione o aluno, o livro e informe a data de devolução."
        }), 400

    try:
        with get_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO emprestimos (id_aluno, id_livro, data_devolucao, devolvido)
                VALUES (?, ?, ?, 0)
            """, (id_usuario, id_livro, data_devolucao))
            conn.commit()
        return jsonify({"status": "sucesso", "mensagem": "Empréstimo registrado!"}), 201
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": str(e)}), 500

@app.route('/api/emprestimos/<int:id_emp>/devolver', methods=['PUT'])
def devolver_emprestimo(id_emp):
    """Rota usada pelo front para marcar um empréstimo como devolvido, sem apagar o histórico."""
    with get_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE emprestimos SET devolvido = 1 WHERE id = ?", (id_emp,))
        conn.commit()
    return jsonify({"status": "sucesso", "mensagem": "Devolução realizada!"}), 200

@app.route('/api/emprestimos/<int:id_emp>', methods=['DELETE'])
def deletar_emprestimo(id_emp):
    with get_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM emprestimos WHERE id=?", (id_emp,))
        conn.commit()
    return jsonify({"status": "sucesso", "mensagem": "Empréstimo removido!"}), 200

# --- MURAL PÚBLICO ---
@app.route('/api/mural', methods=['GET'])
def listar_mural():
    with get_conexao() as conn:
        cursor = conn.cursor()

        # Calcula o limite de 24 horas atrás com base no horário atual
        limite = (datetime.now() - timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')

        # Apaga automaticamente todas as mensagens com mais de 24 horas
        cursor.execute("DELETE FROM mural_mensagens WHERE data_envio < ?", (limite,))
        conn.commit()

        # Retorna apenas as mensagens válidas (com menos de 24h)
        cursor.execute("""
            SELECT
                id,
                id_usuario,
                nome_usuario,
                conteudo,
                conteudo AS mensagem,
                strftime('%H:%M', data_envio) as hora
            FROM mural_mensagens
            ORDER BY id ASC
        """)
        return jsonify([dict(row) for row in cursor.fetchall()]), 200

@app.route('/api/mural', methods=['POST'])
def criar_mensagem_mural():
    dados = request.get_json() or {}

    # Tratativa otimizada para capturar o conteúdo independentemente da chave enviada pelo front-end
    conteudo = dados.get('conteudo') or dados.get('mensagem') or dados.get('texto')

    if not conteudo:
        return jsonify({"status": "erro", "mensagem": "O conteúdo da mensagem não pode estar vazio."}), 400

    with get_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO mural_mensagens (id_usuario, nome_usuario, conteudo)
            VALUES (?, ?, ?)
        """, (dados.get('id_usuario'), dados.get('nome_usuario'), conteudo))
        conn.commit()
    return jsonify({"status": "sucesso"}), 201

# --- BUGS ---
@app.route('/api/bugs', methods=['POST'])
def reportar_bug():
    dados = request.get_json() or {}
    with get_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO bug_reports (id_usuario, nome_usuario, categoria, descricao)
            VALUES (?, ?, ?, ?)
        """, (dados.get('id_usuario'), dados.get('nome_usuario'), dados.get('categoria'), dados.get('descricao')))
        conn.commit()
    return jsonify({"status": "sucesso"}), 201

if __name__ == '__main__':
    app.run(debug=True, port=5000)