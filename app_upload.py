import streamlit as st
import os

st.title("Upload de Planilhas - Chefe de Gabinete")

# Pasta onde os arquivos serão salvos
UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Senha para upload (opcional)
senha_correta = "chefe123"
senha_input = st.text_input("Digite a senha para enviar planilha:", type="password")

# Upload do arquivo
uploaded_file = st.file_uploader("Selecione o arquivo Excel ou CSV", type=["xlsx","csv"])

if uploaded_file is not None and senha_input == senha_correta:
    file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"Arquivo salvo com sucesso: {uploaded_file.name}")
elif uploaded_file is not None and senha_input != senha_correta:
    st.error("Senha incorreta. Você não pode enviar o arquivo.")
