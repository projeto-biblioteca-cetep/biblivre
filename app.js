// Recuperando dependências injetadas
const { db, renderer, auth } = window;

let alunos = db.getAlunos();
let acervo = db.getAcervo();
let emprestimos = db.getEmprestimos();
let usuarioLogado = null;

// Inicializador
window.addEventListener('DOMContentLoaded', () => {
    selecionarPrazoRapido(14);
    renderer.atualizarDropdowns(alunos, acervo);
    renderer.renderAcervoPublico(acervo);
});

// Funções expostas no escopo global para responder aos eventos onclick inline do HTML
window.escolherPerfil = (perfil) => auth.escolherPerfil(perfil);
window.voltarParaSplash = (perfil) => auth.voltarParaSplash(perfil);
window.logout = () => {
    auth.logout();
    usuarioLogado = null;
};

window.autenticarAluno = (event) => {
    auth.autenticarAluno(event, alunos, (aluno) => {
        usuarioLogado = aluno;
        renderer.renderLeituraAluno(emprestimos, acervo, usuarioLogado);
    });
};

window.autenticarAdmin = (event) => auth.autenticarAdmin(event);

window.alternarFormatoInput = function() {
    const formato = document.getElementById('formatoLivro').value;
    const inputLocal = document.getElementById('estanteLivro');
    if (formato === 'Digital') {
        inputLocal.placeholder = "URL do PDF (Ex: https://link.com/livro.pdf)";
    } else {
        inputLocal.placeholder = "Localização Física (Ex: Estante B-4)";
    }
};

window.selecionarPrazoRapido = function(dias) {
    const hoje = new Date();
    hoje.setDate(hoje.getDate() + dias);
    const dataFormatada = hoje.toISOString().split('T')[0];
    document.getElementById('dataDevolucaoForm').value = dataFormatada;
};

// Cadastro e Empréstimos
window.cadastrarAluno = function(event) {
    event.preventDefault();
    const nome = document.getElementById('nomeAluno').value;
    const senha = document.getElementById('senhaAluno').value;
    const serie = document.getElementById('serieAluno').value;
    const turma = document.getElementById('turmaAluno').value;

    alunos.push({ nome, senha, serie, turma });
    db.saveAlunos(alunos);
    
    alert(`Aluno ${nome} matriculado! Ele já pode acessar.`);
    event.target.reset();
    renderer.atualizarDropdowns(alunos, acervo);
};

window.cadastrarLivro = function(event) {
    event.preventDefault();
    const titulo = document.getElementById('tituloLivro').value;
    const autor = document.getElementById('autorLivro').value;
    const formato = document.getElementById('formatoLivro').value;
    const genero = document.getElementById('generoLivro').value;
    const local = document.getElementById('estanteLivro').value;
    const icone = document.getElementById('iconeLivro').value;

    const novoLivro = { id: Date.now(), titulo, autor, formato, genero, local, icone };
    acervo.push(novoLivro);
    db.saveAcervo(acervo);

    alert('O livro foi inserido com sucesso!');
    event.target.reset();
    renderer.atualizarDropdowns(alunos, acervo);
    renderer.renderAcervoPublico(acervo);
};

window.registrarEmprestimo = function(event) {
    event.preventDefault();
    const alunoNome = document.getElementById('selectAluno').value;
    const livroId = parseInt(document.getElementById('selectLivro').value);
    const dataDevolucao = document.getElementById('dataDevolucaoForm').value;

    if(!alunoNome || !livroId || !dataDevolucao) return alert('Por favor, preencha todos os campos.');

    emprestimos.push({ aluno: alunoNome, livroId, dataDevolucao });
    db.saveEmprestimos(emprestimos);

    alert('Empréstimo concedido com sucesso!');
    if (usuarioLogado && usuarioLogado.nome.toLowerCase() === alunoNome.toLowerCase()) {
        renderer.renderLeituraAluno(emprestimos, acervo, usuarioLogado);
    }
};