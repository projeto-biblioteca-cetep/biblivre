const renderer = {
    renderAcervoPublico(acervo) {
        const container = document.getElementById('gridAcervoPublico');
        if (!container) return;
        container.innerHTML = '';

        acervo.forEach(livro => {
            const badgeStyle = livro.formato === 'Digital' 
                ? 'bg-emerald-500/15 text-emerald-300 border border-emerald-500/20' 
                : 'bg-indigo-500/15 text-indigo-300 border border-indigo-500/20';

            const card = `
                <div class="bg-slate-900/60 border border-slate-800 p-5 rounded-2xl flex flex-col justify-between hover:border-slate-700/80 transition-all">
                    <div>
                        <span class="text-3xl">${livro.icone}</span>
                        <h4 class="font-bold text-white text-md mt-2">${livro.titulo}</h4>
                        <p class="text-xs text-slate-400 mt-1">Por: ${livro.autor}</p>
                        <span class="inline-block mt-3 text-[10px] font-semibold tracking-wider uppercase px-2.5 py-1 rounded-md ${badgeStyle}">
                            ${livro.formato} - ${livro.genero}
                        </span>
                    </div>
                    <p class="text-xs text-slate-500 mt-4 pt-3 border-t border-slate-800/80">Local: <span class="text-slate-300">${livro.formato === 'Digital' ? 'Nuvem Virtual' : livro.local}</span></p>
                </div>
            `;
            container.innerHTML += card;
        });
    },

    renderLeituraAluno(emprestimos, acervo, usuarioLogado) {
        const container = document.getElementById('listaLivrosAluno');
        if (!container) return;
        container.innerHTML = '';

        const meusEmprestimos = emprestimos.filter(emp => emp.aluno.toLowerCase() === usuarioLogado.nome.toLowerCase());
        
        if (meusEmprestimos.length === 0) {
            container.innerHTML = `<p class="text-xs text-slate-400 col-span-full py-4 text-center">Nenhum livro (físico ou digital) está em sua posse hoje.</p>`;
            return;
        }

        meusEmprestimos.forEach(emp => {
            const livro = acervo.find(l => l.id === emp.livroId);
            if (livro) {
                const dataPartes = emp.dataDevolucao.split('-');
                const dataFormatada = `${dataPartes[2]}/${dataPartes[1]}/${dataPartes[0]}`;

                const acaoBotao = livro.formato === 'Digital'
                    ? `<a href="${livro.local}" target="_blank" class="flex items-center justify-center gap-1.5 w-full bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold py-2.5 rounded-xl transition-all shadow-md mt-4">
                        <span class="material-icons text-sm">picture_as_pdf</span> Ler PDF Online
                       </a>`
                    : `<div class="bg-indigo-950/40 border border-indigo-800/50 rounded-xl p-3 mt-4 text-center">
                        <p class="text-[10px] text-indigo-300 font-medium">Devolver na Estante Física: <span class="font-bold">${livro.local}</span></p>
                       </div>`;

                const card = `
                    <div class="bg-slate-900 border border-slate-800 p-5 rounded-2xl flex flex-col justify-between">
                        <div>
                            <div class="flex items-center justify-between">
                                <span class="text-3xl">${livro.icone}</span>
                                <span class="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                                    ${livro.formato}
                                </span>
                            </div>
                            <h4 class="font-bold text-white text-md mt-3">${livro.titulo}</h4>
                            <p class="text-xs text-slate-400 mt-1">Por: ${livro.autor}</p>
                        </div>
                        <div>
                            <div class="flex items-center gap-2 mt-4 pt-3 border-t border-slate-800/80 text-xs text-slate-400">
                                <span class="material-icons text-sm text-pink-400">event</span>
                                <span>Devolver até: <strong class="text-pink-300">${dataFormatada}</strong></span>
                            </div>
                            ${acaoBotao}
                        </div>
                    </div>
                `;
                container.innerHTML += card;
            }
        });
    },

    atualizarDropdowns(alunos, acervo) {
        const selectAluno = document.getElementById('selectAluno');
        const selectLivro = document.getElementById('selectLivro');

        if (selectAluno && selectLivro) {
            selectAluno.innerHTML = alunos.map(aluno => 
                `<option value="${aluno.nome}">${aluno.nome} (${aluno.serie} ${aluno.turma})</option>`
            ).join('');

            selectLivro.innerHTML = acervo.map(livro => 
                `<option value="${livro.id}">${livro.titulo} [${livro.formato}]</option>`
            ).join('');
        }
    }
};

window.renderer = renderer;