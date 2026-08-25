# database.py
import sqlite3

NOME_BANCO = 'biblivre.db'
SUPABASE_DB_SENHA = 'Jl0kkWB34rxNbMeY'

def get_conexao():
    """Abre e retorna uma conexão com o banco SQLite."""
    conn = sqlite3.connect(NOME_BANCO)
    # Garante suporte a dicionários no retorno e ativa Chaves Estrangeiras (FK)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def inicializar_banco():
    """Cria as tabelas caso não existam."""
    with get_conexao() as conn:
        cursor = conn.cursor()
        
        # Tabela Usuários
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cadastro TEXT NOT NULL UNIQUE,
            matricula TEXT,
            ano TEXT,
            turma TEXT,
            cpf TEXT,
            telefone TEXT,
            email TEXT NOT NULL UNIQUE,
            endereco TEXT,
            senha TEXT NOT NULL,
            tipo TEXT CHECK(tipo IN ('aluno', 'admin', 'dev')) NOT NULL DEFAULT 'aluno',
            foto TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ''')

        # Tabela Livros
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS livros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            genero TEXT NOT NULL,
            icone TEXT NOT NULL DEFAULT '📖',
            estante TEXT NOT NULL,
            formato TEXT CHECK(formato IN ('Físico', 'Digital')) NOT NULL DEFAULT 'Físico',
            local TEXT NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ''')

        # Tabela Empréstimos
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS emprestimos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_aluno INTEGER NOT NULL,
            id_livro INTEGER NOT NULL,
            data_devolucao TEXT NOT NULL,
            data_emprestimo TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_aluno) REFERENCES usuarios(id) ON DELETE CASCADE,
            FOREIGN KEY (id_livro) REFERENCES livros(id) ON DELETE CASCADE
        );
        ''')
        conn.commit()
    print("✅ Banco inicializado com sucesso!")