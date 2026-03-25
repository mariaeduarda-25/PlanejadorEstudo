import streamlit as st
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.groq import Groq
from datetime import datetime
import os

load_dotenv()

st.set_page_config(page_title="Planejador de Estudos", page_icon="📚", layout="wide")

def criar_agente_estudos():
    return Agent(
        model=Groq(id="llama-3.3-70b-versatile"),
        description="Você é um Mentor Acadêmico Especialista em Tomada de Decisão Estratégica e Matemática de Horários.",
        instructions=[
            "### 1. PROTOCOLO DE TOMADA DE DECISÃO (RIGOROSO)",
            "A. ANÁLISE DE CRITICIDADE: Calcule o peso de cada matéria. Prioridade Crítica = Prova em < 3 dias ou Desempenho < 50%.",
            "B. REGRA DO CORTE (PRUNING): Se o tempo total disponível for insuficiente (< 4 horas) e houver matérias 'Críticas', você DEVE ignorar completamente matérias com Desempenho > 80% e Prova > 7 dias.",
            "C. ALOCAÇÃO DE RECURSOS: Matérias 'Críticas' devem receber pelo menos 70% do tempo total.",
            
            "### 2. PRECISÃO MATEMÁTICA (OBRIGATÓRIO)",
            "- A soma total dos minutos de estudo na tabela DEVE ser EXATAMENTE igual ao 'Tempo Total Disponível' informado pelo usuário.",
            "- Não deixe 'buracos' ou minutos sobrando no cronograma.",
            
            "### 3. REGRAS DE FORMATAÇÃO",
            "- Use títulos (##) e ícones.",
            "- SEÇÃO '🧠 Raciocínio de Priorização': Explique explicitamente quais matérias você decidiu IGNORAR e por quê.",
            "- TABELA: | Horário (Início - Fim) | Disciplina | Objetivo | Técnica |.",
            "- Certifique-se de que o primeiro horário comece no início do turno selecionado (ex: Noite às 19:00)."
        ],
        markdown=True
    )

st.title("🎓 Planejador de Estudos Inteligente")
st.write("---")

# Layout de Colunas para a Rotina
st.write("### 🕒 Configuração da Rotina")
c1, c2 = st.columns(2)
with c1:
    turnos = st.multiselect("Turnos disponíveis para hoje:", ["Manhã", "Tarde", "Noite"], default=["Noite"])
with c2:
    horas_totais = st.number_input("Total de horas para estudar hoje:", 1, 16, 3)

st.divider()

if "disciplinas" not in st.session_state:
    st.session_state.disciplinas = []

# Formulário de Adição
st.write("### 📖 Cadastro de Disciplinas")
col_a, col_b = st.columns(2)

with col_a:
    nome = st.text_input("Nome da Disciplina", placeholder="Ex: Cálculo II")
    data_p = st.date_input("Data da Prova", format="DD/MM/YYYY")
    dif = st.slider("Grau de Dificuldade (1-10)", 1, 10, 5)

with col_b:
    teve_prova = st.radio("Já realizou alguma avaliação?", ["Não", "Sim"], horizontal=True)
    nota = st.number_input("Qual foi seu desempenho médio? (%)", 0, 100, 0, disabled=(teve_prova == "Não"))

if st.button("➕ Adicionar à Lista"):
    if nome:
        st.session_state.disciplinas.append({
            "Disciplina": nome,
            "Dificuldade": dif,
            "Data": data_p.strftime("%d/%m/%Y"),
            "Desempenho": f"{nota}%" if teve_prova == "Sim" else "N/A"
        })
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
            with st.spinner("Analisando prioridades..."):
                try:
                    agente = criar_agente_estudos()
                    
                    # MELHORIA: Contexto mais estruturado para evitar erros de cálculo da IA
                    contexto = f"""
                    DADOS PARA DECISÃO:
                    - DATA DE HOJE: {datetime.now().strftime('%d/%m/%Y')}
                    - TEMPO TOTAL DISPONÍVEL: {horas_totais} horas ({horas_totais * 60} minutos)
                    - TURNOS: {', '.join(turnos)}
                    - DISCIPLINAS CADASTRADAS: {st.session_state.disciplinas}
                    
                    TAREFA: Gere o plano garantindo que a soma dos minutos na tabela seja {horas_totais * 60} minutos.
                    """
                    
                    resp = agente.run(contexto)
                    st.success("Plano Estratégico Gerado!")
                    st.markdown(resp.content)
                    
                except Exception as e:
                    st.error(f"Erro: {e}")