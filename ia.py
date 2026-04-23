# To run this code you need to install the following dependencies:
# pip install google-genai

import os
from google import genai
from google.genai import types


def generate():
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    model = "gemini-3-flash-preview"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""pront de sistema
"""),
            ],
        ),
        types.Content(
            role="model",
            parts=[
                types.Part.from_text(text="""**Defining System Prompt Requests**

I'm now identifying that the user's \"pront de sistema\" probably indicates a request for a system prompt. It seems they want either a definition or examples of how to construct one. I'm focusing on clarifying that aspect to offer relevant guidance and examples.


"""),
                types.Part.from_text(text="""O termo **\"System Prompt\"** (ou Prompt de Sistema) refere-se às instruções iniciais e permanentes que definem a **identidade, o comportamento e as limitações** de uma Inteligência Artificial.

Se você está procurando um modelo para configurar sua própria IA ou quer entender como criar um bom prontuário, aqui está um guia e alguns exemplos:

---

### 1. Estrutura de um Bom System Prompt
Para que a IA funcione bem, o prompt de sistema deve cobrir quatro pilares:
1.  **Perfil (Quem você é):** Define a \"persona\" (ex: \"Você é um professor de matemática\").
2.  **Objetivo (O que você faz):** Define a tarefa principal (ex: \"Sua missão é resolver equações passo a passo\").
3.  **Tom e Estilo (Como você fala):** (ex: \"Use uma linguagem simples, encorajadora e evite gírias\").
4.  **Restrições (O que você não faz):** (ex: \"Nunca dê a resposta final sem antes explicar o raciocínio\").

---

### 2. Exemplos de System Prompts para Copiar

#### Exemplo A: Assistente de Programação (Focado em Código Limpo)
> \"Você é um desenvolvedor Senior Full Stack especializado em arquitetura de software e código limpo. Sua tarefa é ajudar o usuário a escrever, depurar e otimizar código. Sempre priorize a legibilidade e os princípios SOLID. Se o código fornecido tiver vulnerabilidades de segurança, aponte-as imediatamente. Responda de forma técnica e objetiva, usando blocos de código Markdown.\"

#### Exemplo B: Professor Particular (Didático)
> \"Você é um tutor acadêmico paciente e didático. Seu objetivo é ajudar o aluno a aprender, não apenas dar a resposta pronta. Quando o aluno fizer uma pergunta, comece testando o conhecimento dele sobre o assunto. Use analogias do cotidiano para explicar conceitos complexos. Mantenha um tom encorajador e calmo.\"

#### Exemplo C: Redator de Marketing (Copywriter)
> \"Você é um especialista em copywriting e marketing digital com foco em conversão. Sua linguagem deve ser persuasiva, direta e adaptada ao público-alvo brasileiro. Use gatilhos mentais como escassez e autoridade. Sempre que escrever um texto, ofereça três variações de títulos chamativos.\"

---

### 3. Dicas para Criar o Seu
Ao escrever o seu \"Pront de Sistema\", tente ser o mais específico possível:

*   **Defina o Formato de Saída:** \"Responda sempre em tópicos\" ou \"Responda em formato JSON\".
*   **Determine o Idioma:** \"Responda sempre em Português do Brasil, mesmo que a pergunta seja em outro idioma\".
*   **Estabeleça Limites de Ética/Segurança:** \"Não forneça opiniões políticas\" ou \"Não gere conteúdo ofensivo\".
*   **Dê Exemplos (Few-Shot):** Inclua um exemplo de como você quer que a resposta seja formatada dentro do próprio prompt de sistema.

---

**Você gostaria que eu escrevesse um System Prompt específico para alguma função?** (Ex: para atendimento ao cliente, análise de dados, criação de RPG, etc.) Basta me dizer o objetivo!"""),
            ],
        ),
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""INSERT_INPUT_HERE"""),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_level="HIGH",
        ),
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if text := chunk.text:
            print(text, end="")

if __name__ == "__main__":
    generate()


