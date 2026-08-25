const auth = {
    escolherPerfil(perfil) {
        document.getElementById('splashScreen').classList.add('hidden');
        if (perfil === 'aluno') {
            document.getElementById('modalAluno').classList.remove('hidden');
        } else if (perfil === 'admin') {
            document.getElementById('modalAdmin').classList.remove('hidden');
        }
    },

    voltarParaSplash(perfilAtual) {
        if (perfilAtual === 'aluno') {
            document.getElementById('modalAluno').classList.add('hidden');
        } else {
            document.getElementById('modalAdmin').classList.add('hidden');
        }
        document.getElementById('splashScreen').classList.remove('hidden');
    },

    autenticarAluno(event, alunos, onSuccess) {
        event.preventDefault();
        const nome = document.getElementById('alunoNomeLogin').value;
        const senha = document.getElementById('alunoSenhaLogin').value;

        const alunoEncontrado = alunos.find(a => a.nome.toLowerCase() === nome.toLowerCase() && a.senha === senha);

        if(alunoEncontrado) {
            document.getElementById('badgeModo').innerText = `Modo Aluno: ${alunoEncontrado.nome}`;
            document.getElementById('badgeModo').className = "text-[10px] bg-emerald-500/20 text-emerald-300 px-2.5 py-0.5 rounded-full font-medium ml-2 border border-emerald-500/30";
            
            document.getElementById('nomeAlunoAtivo').innerText = alunoEncontrado.nome;
            document.getElementById('secaoLeituraAluno').classList.remove('hidden');
            document.getElementById('modalAluno').classList.add('hidden');
            
            onSuccess(alunoEncontrado);
        } else {
            alert('Matrícula ou Senha incorretas! Solicite seu cadastro na secretaria (Modo Admin).');
        }
    },

    autenticarAdmin(event) {
        event.preventDefault();
        const user = document.getElementById('loginUsuario').value;
        const pass = document.getElementById('loginSenha').value;

        if(user === 'admin' && pass === '1234') {
            document.getElementById('secaoAdmin').classList.remove('hidden');
            document.getElementById('badgeModo').innerText = "Painel Administrador";
            document.getElementById('badgeModo').className = "text-[10px] bg-pink-500/20 text-pink-300 px-2.5 py-0.5 rounded-full font-medium ml-2 border border-pink-500/30";
            document.getElementById('modalAdmin').classList.add('hidden');
        } else {
            alert('Acesso restrito para administradores credenciados.');
        }
    },

    logout() {
        document.getElementById('secaoLeituraAluno').classList.add('hidden');
        document.getElementById('secaoAdmin').classList.add('hidden');
        document.getElementById('badgeModo').innerText = "Modo Visitante";
        document.getElementById('badgeModo').className = "text-[10px] bg-slate-800 text-slate-400 px-2.5 py-0.5 rounded-full font-medium ml-2 border border-slate-700/50";
        
        document.getElementById('alunoNomeLogin').value = '';
        document.getElementById('alunoSenhaLogin').value = '';
        document.getElementById('loginUsuario').value = '';
        document.getElementById('loginSenha').value = '';

        document.getElementById('splashScreen').classList.remove('hidden');
    }
};

window.auth = auth;