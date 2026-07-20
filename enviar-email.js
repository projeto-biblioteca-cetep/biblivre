import { Resend } from 'resend';

// Inicializa o Resend com a chave que virá das variáveis de ambiente da Vercel
const resend = new Resend(process.env.RESEND_API_KEY);

export default async function handler(req, res) {
    // Garante que a requisição seja do tipo POST
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Método não permitido' });
    }

    const { email, assunto, mensagem } = req.body;

    try {
        const data = await resend.emails.send({
            from: 'Seu Site <onboarding@resend.dev>',
            to: ['seu_email_pessoal@gmail.com'],
            reply_to: email,
            subject: assunto,
            html: `<p><strong>Novo contato de:</strong> ${email}</p><p>${mensagem}</p>`
        });

        return res.status(200).json({ success: true, data });
    } catch (error) {
        console.error(error);
        return res.status(500).json({ success: false, error: error.message });
    }
}