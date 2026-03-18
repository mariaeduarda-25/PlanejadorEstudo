import streamlit as st
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.groq import Groq
from datetime import datetime
import os

load_dotenv()

st.set_page_config(page_title="IA Advisor de Estudos", page_icon="📚", layout="wide")


def criar_agente_estudos():
    return Agent(
        model=Groq(id="llama-3.3-70b-versatile"),
        description="Você é um Mentor Acadêmico Especialista em Otimização de Aprendizado.",
        instructions=[
            "Analise a lista de disciplinas, turnos e horas informadas.",
            "Priorize: 1. Provas próximas, 2. Baixo desempenho + Alta dificuldade.",
            "Crie um plano diário detalhado e motivador.",
            "Retorne a resposta em Markdown bem formatado."
        ],
        markdown=True
    )

st.title("🎓 Planejador de Estudos Inteligente")


st.write("### 🕒 Sua Rotina")
c1, c2 = st.columns(2)
with c1:
    turnos = st.multiselect("Turnos de estudo:", ["Manhã", "Tarde", "Noite"], default=["Manhã"])
with c2:
    horas = st.number_input("Horas diárias de dedicação:", 1, 16, 4)

st.divider()

if "disciplinas" not in st.session_state:
    st.session_state.disciplinas = []

st.write("### 📖 Adicionar Disciplina")
col_a, col_b = st.columns(2)

with col_a:
    nome = st.text_input("Nome da Disciplina", key="input_nome")
    data_p = st.date_input("Data da Prova", format="DD/MM/YYYY")
    dif = st.slider("Dificuldade (1-10)", 1, 10, 5)

with col_b:
 
    teve_prova = st.radio("Já fez prova dessa matéria?", ["Não", "Sim"], horizontal=True)
    

    nota = st.number_input(
        "Desempenho Anterior (%)", 
        0, 100, 0, 
        disabled=(teve_prova == "Não")
    )


if st.button("➕ Adicionar à Lista"):
    if nome:
        st.session_state.disciplinas.append({
            "Disciplina": nome,
            "Dificuldade": dif,
            "Data": data_p.strftime("%d/%m/%Y"),
            "Desempenho": f"{nota}%" if teve_prova == "Sim" else "N/A"
        })
        st.rerun() 
    else:
        st.error("Digite o nome da disciplina.")

st.divider()


if st.session_state.disciplinas:
    st.write("### Suas Disciplinas")
    st.table(st.session_state.disciplinas)
    
    col_btn1, col_btn2 = st.columns([1, 5])
    with col_btn1:
        if st.button("🗑️ Limpar"):
            st.session_state.disciplinas = []
            st.rerun()
    
    with col_btn2:
        if st.button("🚀 GERAR PLANO DE ESTUDOS"):
            with st.spinner("Calculando sua rota de aprovação..."):
                try:
                    agente = criar_agente_estudos()
                    contexto = f"""
                    Turnos: {turnos}, Horas: {horas}/dia.
                    Hoje: {datetime.now().strftime('%d/%m/%Y')}
                    Disciplinas: {st.session_state.disciplinas}
                    """
                    resp = agente.run(contexto)
                    st.markdown(resp.content)
                except Exception as e:
                    st.error(f"Erro: {e}")