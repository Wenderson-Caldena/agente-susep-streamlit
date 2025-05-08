import streamlit as st
from rag_pipeline.query_engine import query_rag

# Lista de usuários permitidos
USERS = {
    "Docinho": "senha123",
    "Sam": "susep2024",
}

st.set_page_config(page_title="Agente SUSEP", layout="centered")

# Inicializa o estado de login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.sidebar.title("🔐 Login")

    username = st.sidebar.text_input("Usuário")
    password = st.sidebar.text_input("Senha", type="password")
    login_button = st.sidebar.button("Entrar")

    if login_button:
        if USERS.get(username) == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()  # <-- força recarregamento da interface após login
        else:
            st.sidebar.warning("Acesso restrito. Informe credenciais válidas.")
    st.stop()  # Impede renderização do conteúdo abaixo se não logado

# Interface do app (chat)
st.title("🧠 Agente de IA - Circular SUSEP 648/2021")
st.write(f"Olá **{st.session_state.username}**, faça uma pergunta sobre a Circular SUSEP 648/2021. O agente irá responder com base nos trechos relevantes do documento.")

user_question = st.text_area("Digite sua pergunta:", height=100)

if st.button("Enviar"):
    if user_question.strip():
        with st.spinner("Consultando a Circular SUSEP 648..."):
            try:
                response = query_rag(user_question)
                st.success("Resposta:")
                st.markdown(response)
            except Exception as e:
                st.error(f"Ocorreu um erro ao processar sua pergunta: {e}")
    else:
        st.warning("Por favor, digite uma pergunta válida.")
