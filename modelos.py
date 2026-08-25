# modelos.py
from database import get_conexao

# --- OPERAÇÕES DE USUÁRIO ---

def realizar_login(cadastro, senha):
    """Valida o login do usuário."""
    with get_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, nome, cadastro, email, tipo, foto 
            FROM usuarios 
            WHERE LOWER(cadastro) = LOWER(?) AND senha = ?;
        ''', (cadastro, senha))
        usuario = cursor.fetchone()
        return dict(usuario) if usuario else None

def cadastrar_aluno(nome, cadastro, email, senha, matricula=None, ano=None, turma=None):
    """Cadastra um novo aluno no banco."""
    try:
        with get_conexao() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO usuarios (nome, cadastro, email, senha, matricula, ano, turma, tipo)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'aluno');
            ''', (nome, cadastro, email, senha, matricula, ano, turma))
            conn.commit()
            return True, "Aluno cadastrado com sucesso!"
    except Exception as e:
        return False, f"Erro ao cadastrar: {e}"

# --- OPERAÇÕES DE LIVROS ---

def listar_livros():
    """Retorna todos os livros cadastrados."""
    with get_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM livros;')
        return [dict(row) for row in cursor.fetchall()]

def cadastrar_livro(titulo, autor, genero, estante, local, formato='Físico', icone='📖'):
    """Insere um novo livro."""
    with get_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO livros (titulo, autor, genero, estante, local, formato, icone)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        ''', (titulo, autor, genero, estante, local, formato, icone))
        conn.commit()
        return cursor.lastrowid

# --- OPERAÇÕES DE EMPRÉSTIMOS ---

def registrar_emprestimo(id_aluno, id_livro, data_devolucao):
    """Registra a saída de um livro para um aluno."""
    with get_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO emprestimos (id_aluno, id_livro, data_devolucao)
            VALUES (?, ?, ?);
        ''', (id_aluno, id_livro, data_devolucao))
        conn.commit()

def monitor_emprestimos():
    """Retorna os empréstimos ativos cruzando os dados das 3 tabelas."""
    with get_conexao() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                e.id AS id_emprestimo,
                u.nome AS nome_aluno,
                u.ano || ' - ' || u.turma AS turma_ano,
                l.icone,
                l.titulo AS titulo_livro,
                e.data_devolucao
            FROM emprestimos e
            JOIN usuarios u ON e.id_aluno = u.id
            JOIN livros l ON e.id_livro = l.id;
        ''')
        return [dict(row) for row in cursor.fetchall()]