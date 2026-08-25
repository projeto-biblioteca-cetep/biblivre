
    async function perguntarIA(e) {
        e.preventDefault();
        const input = document.getElementById('chatInput');
        const texto = input.value.trim();
        if(!texto) return;

        // INSIRA A SUA CHAVE DA API AQUI
        const API_KEY = 'AQ.Ab8RN6JI4w8UHjnVjOAwk19rbS77wA5adj_nbsnqNXzbrG3VqQ'; 

        adicionarBolhaChat(texto, true);
        input.value = '';

        const container = document.getElementById('chatConversa');
        const loadId = 'loading-' + Date.now();
        const typingDiv = document.createElement('div');
        typingDiv.id = loadId;
        typingDiv.className = 'flex items-start gap-2 mb-4';
        typingDiv.innerHTML = `
            <div class="bg-indigo-500 w-8 h-8 rounded-full flex items-center justify-center shrink-0 shadow-md"><span class="material-icons text-white text-xs">smart_toy</span></div>
            <div class="bg-slate-900 border border-slate-850 p-3 rounded-2xl rounded-tl-none text-xs sm:text-sm text-slate-200 flex items-center gap-1.5 shadow-md h-10">
                <div class="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce"></div>
                <div class="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" style="animation-delay: 0.15s"></div>
                <div class="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" style="animation-delay: 0.3s"></div>
            </div>
        `;
        container.appendChild(typingDiv);
        container.scrollTop = container.scrollHeight;

        try {
            // Endpoint ajustado para o modelo ativo no Google AI Studio
            const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key=${API_KEY}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    contents: [{
                        parts: [{
                            text: `Você é o assistente virtual do projeto Biblivre. Responda de forma clara, prestativa e educacional à seguinte mensagem do usuário: ${texto}`
                        }]
                    }]
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error?.message || 'Erro de autenticação ou chave inválida.');
            }

            const respostaIA = data.candidates[0].content.parts[0].text;
            
            // Formata quebras de linha para exibição no HTML
            const respostaFormatada = respostaIA.replace(/\n/g, '<br>');

            const el = document.getElementById(loadId);
            if(el) el.remove();
            adicionarBolhaChat(respostaFormatada, false);

        } catch (error) {
            console.error("Erro na requisição:", error);
            const el = document.getElementById(loadId);
            if(el) el.remove();
            
            adicionarBolhaChat(`⚠️ <b>Erro de Conexão:</b> ${error.message}<br><small>Verifique sua chave da API do Google AI Studio.</small>`, false);
        }
    }