import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
from datetime import datetime
import os

load_dotenv()
CHAVE_API = os.getenv("GOOGLE_API_KEY")

if CHAVE_API:
    genai.configure(api_key=CHAVE_API)
else:
    st.error("Erro: GOOGLE_API_KEY não encontrada no arquivo .env")

st.set_page_config(page_title="Planejador de Estudos", page_icon="📚", layout="wide")


def criar_modelo_estudos():
    instrucoes = (
        "Você é um Mentor Acadêmico Especialista em Tomada de Decisão Estratégica.\n\n"
        "Sua resposta DEVE seguir rigorosamente esta estrutura de 5 seções:\n\n"
        "1. ## 📊 Análise Inicial\n"
        "Breve resumo do cenário atual: data, tempo disponível e criticidade geral.\n\n"
        "2. ## 🧠 Raciocínio de Priorização\n"
        "Explique a 'Regra do Corte'. Liste quais matérias você decidiu IGNORAR e por quê "
        "(ex: Prova > 7 dias e Desempenho > 80%).\n\n"
        "3. ## 🕒 Alocamento de Recursos\n"
        "Mostre como os minutos foram divididos. Matérias 'Críticas' devem receber pelo menos 70% do tempo total\n"
        "4. ## 📝 Estratégia Pedagógica\n"
        "Sugira técnicas (Mapas Mentais, Questões) para cada bloco de estudo.\n\n"
        "5. ## 📅 Plano de Estudos\n"
        "Crie uma tabela Markdown: | Horário| Disciplina | Objetivo | Técnica |\n"
        "REGRAS MATEMÁTICAS:\n"
        "- A soma dos minutos na tabela deve ser EXATAMENTE o tempo total informado.\n"
        "- O plano deve começar no horário inicial do primeiro turno selecionado.\n"
        "- Não ultrapasse o limite de tempo sob nenhuma hipótese"
    )

    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash-lite", system_instruction=instrucoes
    )
    return model



st.title("🎓 Planejador de Estudos Inteligente")
st.write("---")

st.write("### 🕒 Configuração da Rotina")
c1, c2 = st.columns(2)
with c1:
    turnos = st.multiselect(
        "Turnos disponíveis para hoje:", ["Manhã", "Tarde", "Noite"], default=["Noite"]
    )
with c2:
    horas_totais = st.number_input("Total de horas para estudar hoje:", 1, 16, 3)

st.divider()

if "disciplinas" not in st.session_state:
    st.session_state.disciplinas = []

st.write("### 📖 Cadastro de Disciplinas")
col_a, col_b = st.columns(2)

with col_a:
    nome = st.text_input("Nome da Disciplina", placeholder="Ex: Cálculo II")
    data_p = st.date_input("Data da Prova", format="DD/MM/YYYY")
    dif = st.slider("Grau de Dificuldade (1-10)", 1, 10, 5)

with col_b:
    teve_prova = st.radio(
        "Já realizou alguma avaliação?", ["Não", "Sim"], horizontal=True
    )
    nota = st.number_input(
        "Qual foi seu desempenho médio? (%)", 0, 100, 0, disabled=(teve_prova == "Não")
    )

if st.button("➕ Adicionar à Lista"):
    if nome:
        st.session_state.disciplinas.append(
            {
                "Disciplina": nome,
                "Dificuldade": dif,
                "Data": data_p.strftime("%d/%m/%Y"),
                "Desempenho": f"{nota}%" if teve_prova == "Sim" else "N/A",
            }
        )
        st.rerun()

st.divider()

if st.session_state.disciplinas:
    st.write("### 📋 Painel de Matérias")
    st.table(st.session_state.disciplinas)

    col_btn1, col_btn2 = st.columns([1, 5])
    with col_btn1:
        if st.button("🗑️ Limpar"):
            st.session_state.disciplinas = []
            st.rerun()

    with col_btn2:
        if st.button("🚀 GERAR PLANO E TOMAR DECISÃO"):
            if not turnos:
                st.warning("Selecione pelo menos um turno!")
            else:
                with st.spinner("Gemini calculando estratégia..."):
                    try:      
                        model = criar_modelo_estudos()
                        horarios_turnos = {
                            "Manhã": "08:00",
                            "Tarde": "13:00",
                            "Noite": "19:00",
                        }
                        horario_inicio = horarios_turnos.get(turnos[0], "08:00")

                        contexto = f"""
                        DADOS PARA DECISÃO:
                        - DATA DE HOJE: {datetime.now().strftime('%d/%m/%Y')}
                        - TEMPO TOTAL: {horas_totais} horas ({horas_totais * 60} minutos)
                        - TURNOS: {', '.join(turnos)}
                        - HORÁRIO DE INÍCIO: {horario_inicio}
                        - DISCIPLINAS: {st.session_state.disciplinas}

                        TAREFA: Gere o plano completo com as 5 seções obrigatórias.
                        """
                        response = model.generate_content(contexto)

                        st.success("Plano Estratégico Gerado com Sucesso!")
                        st.markdown(response.text)

                    except Exception as e:
                        st.error(f"Erro ao processar plano: {e}")
