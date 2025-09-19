import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from glob import glob

# ------------------- CONFIGURAÇÃO -------------------
st.set_page_config(
    page_title="Painel de Receitas Municipais",
    layout="wide"
)

# Título centralizado
st.markdown("<h1 style='text-align: center;'>📊 Painel de Gestão de Receitas Municipais</h1>", unsafe_allow_html=True)

# ------------------- LISTAR PLANILHAS -------------------
# Diretório onde o app de upload salva as planilhas
UPLOAD_DIR = "uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

files = glob(os.path.join(UPLOAD_DIR, "*.xlsx")) + glob(os.path.join(UPLOAD_DIR, "*.csv"))

if not files:
    st.error(f"Nenhuma planilha encontrada em {UPLOAD_DIR}. Use o app de upload para enviar uma planilha.")
    st.stop()

# Dropdown para selecionar planilha
selected_file = st.selectbox("Escolha a planilha para visualizar:", files)

# ------------------- CARREGAR PLANILHA -------------------
if selected_file.endswith(".csv"):
    df = pd.read_csv(selected_file, delimiter=";|,", engine="python")
else:
    df = pd.read_excel(selected_file)

df.columns = df.columns.str.strip()

# ------------------- FILTROS EM QUADRO AZUL -------------------
col_exercicio, col_instituicao, col_competencia, col_receita = st.columns([1.5,2,2,2])

with col_exercicio:
    exercicios = st.multiselect(
        "Exercício", options=df["EXERCICIO"].unique(), default=df["EXERCICIO"].unique()
    )

with col_instituicao:
    instituicoes = st.multiselect(
        "Instituição", options=df["INSTITUIÇÃO"].unique(), default=df["INSTITUIÇÃO"].unique()
    )

with col_competencia:
    competencias = st.multiselect(
        "Competência", options=df["COMPETENCIA"].unique(), default=df["COMPETENCIA"].unique()
    )

with col_receita:
    receitas = st.multiselect(
        "Receita", options=df["RECEITA"].unique(), default=df["RECEITA"].unique()
    )

st.markdown("</div>", unsafe_allow_html=True)

# ------------------- APLICAR FILTROS -------------------
df_filtered = df[
    (df["EXERCICIO"].isin(exercicios)) &
    (df["INSTITUIÇÃO"].isin(instituicoes)) &
    (df["COMPETENCIA"].isin(competencias)) &
    (df["RECEITA"].isin(receitas))
]

# ------------------- GRÁFICO 1 - Ranking de Receitas -------------------
fig1 = px.bar(
    df_filtered.groupby("INSTITUIÇÃO", as_index=False)["VALOR"].sum(),
    x="INSTITUIÇÃO", y="VALOR",
    color="INSTITUIÇÃO",
    text=df_filtered.groupby("INSTITUIÇÃO", as_index=False)["VALOR"].sum()["VALOR"].apply(
        lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    ),
    title="<b>🏆 Ranking de Receitas por Instituição</b>"
)
fig1.update_traces(textposition='inside', insidetextanchor='middle')
fig1.update_layout(title_font_size=22)
st.plotly_chart(fig1, use_container_width=True)

# ------------------- GRÁFICO 2 - Evolução Mensal Detalhada -------------------
fig2 = go.Figure()
line_styles = ['solid', 'dash', 'dot', 'dashdot']
colors = px.colors.qualitative.Safe  # Uma cor por município

for i, municipio in enumerate(df_filtered["INSTITUIÇÃO"].unique()):
    df_mun = df_filtered[df_filtered["INSTITUIÇÃO"]==municipio]
    color = colors[i % len(colors)]
    for j, receita in enumerate(df_mun["RECEITA"].unique()):
        df_r = df_mun[df_mun["RECEITA"]==receita].groupby("COMPETENCIA", as_index=False)["VALOR"].sum()
        fig2.add_trace(go.Scatter(
            x=df_r["COMPETENCIA"],
            y=df_r["VALOR"],
            mode='lines+markers',
            name=f"{municipio} - {receita}",
            line=dict(color=color, dash=line_styles[j % len(line_styles)]),
            marker=dict(size=6)
        ))

fig2.update_layout(
    title="<b>📈 Evolução Mensal da Receita por Município e Receita</b>",
    yaxis_title="Valor (R$)",
    xaxis_title="Competência",
    legend_title="Município - Receita",
    template="plotly_white"
)
st.plotly_chart(fig2, use_container_width=True)

# ------------------- GRÁFICO 3 - Comparação por Receita -------------------
st.markdown("### 🏙️ Comparação de Receitas entre Instituições")
df_receitas_total = df_filtered.groupby(["INSTITUIÇÃO", "RECEITA"], as_index=False)["VALOR"].sum()
fig3 = px.bar(
    df_receitas_total,
    x="RECEITA",
    y="VALOR",
    color="INSTITUIÇÃO",
    barmode="group",
    text=df_receitas_total["VALOR"].apply(
        lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    )
)
fig3.update_traces(textposition='inside', insidetextanchor='middle')
fig3.update_layout(title_font_size=22)
st.plotly_chart(fig3, use_container_width=True)

# ------------------- GRÁFICO 4 - Participação Percentual -------------------
fig4 = px.pie(
    df_filtered.groupby("INSTITUIÇÃO", as_index=False)["VALOR"].sum(),
    names="INSTITUIÇÃO", values="VALOR",
    title="<b>📊 Participação de Cada Instituição</b>"
)
st.plotly_chart(fig4, use_container_width=True)
