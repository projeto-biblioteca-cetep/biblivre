// Instanciação e persistência do Mock Data no LocalStorage
const db = {
    getAlunos() {
        return JSON.parse(localStorage.getItem('alunos')) || [
            { nome: 'João Silva', senha: '123', serie: '8º Ano', turma: 'A' },
            { nome: 'Maria Souza', senha: '456', serie: '9º Ano', turma: 'B' }
        ];
    },

    saveAlunos(alunos) {
        localStorage.setItem('alunos', JSON.stringify(alunos));
    },

    getAcervo() {
        return JSON.parse(localStorage.getItem('acervo')) || [
            { id: 1, titulo: 'Introdução ao HTML5', autor: 'Ana Clara', formato: 'Digital', genero: 'Tecnologia', local: 'https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf', icone: '📱' },
            { id: 2, titulo: 'Dom Casmurro', autor: 'Machado de Assis', formato: 'Físico', genero: 'Romance', local: 'Estante A-3', icone: '📖' }
        ];
    },

    saveAcervo(acervo) {
        localStorage.setItem('acervo', JSON.stringify(acervo));
    },

    getEmprestimos() {
        return JSON.parse(localStorage.getItem('emprestimos')) || [
            { aluno: 'João Silva', livroId: 1, dataDevolucao: '2026-07-28' }
        ];
    },

    saveEmprestimos(emprestimos) {
        localStorage.setItem('emprestimos', JSON.stringify(emprestimos));
    }
};

// Vinculando ao escopo global para acesso facilitado entre scripts
window.db = db;