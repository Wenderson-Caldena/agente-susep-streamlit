import streamlit as st
from rag_pipeline.query_engine import query_rag

# Lista de usuários permitidos (ex: login:senha)
USERS = {
    "Wend": "senha123",
    "Sam": "susep2024",
    # adicione mais se quiser
}

st.set_page_config(page_title="Agente SUSEP", layout="centered")


st.sidebar.title("🔐 Login")

username = st.sidebar.text_input("Usuário")
password = st.sidebar.text_input("Senha", type="password")

if USERS.get(username) != password:
    st.sidebar.warning("Acesso restrito. Informe credenciais válidas.")
    st.stop()



st.title("🧠 Agente de IA - Circular SUSEP 648/2021")
st.write("Faça uma pergunta sobre a Circular SUSEP 648/2021. O agente irá responder com base nos trechos relevantes do documento.")

# Entrada de pergunta do usuário
user_question = st.text_area("Digite sua pergunta:", height=100)


# Quando o botão é clicado, gera a resposta
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
