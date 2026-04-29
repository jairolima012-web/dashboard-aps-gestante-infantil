import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide", page_title="Dashboard APS Integrado")

# --- 1. CARREGAMENTO DOS DADOS ---

@st.cache_data # Cache para carregar mais rápido
def carregar_dados():
    # Arquivo 1: Consolidado (Indicadores)
    df_indicadores = pd.read_csv("Consolidado_G_I.csv", skiprows=1, encoding="latin1")
    df_indicadores.rename(columns={df_indicadores.columns[0]: "Mês"}, inplace=True)
    df_indicadores.columns = df_indicadores.columns.str.strip()
    
    # Arquivo 2: Classificação (CVAT)
    df_class = pd.read_csv("Classificacao_G_I.csv", encoding="latin1")
    return df_indicadores, df_class

df_ind, df_class = carregar_dados()

# --- 2. SIDEBAR / FILTROS ---

st.sidebar.header("Configurações Gerais")
grupo = st.sidebar.radio("Selecione o Grupo de Análise:", ["Infantil", "Gestação e Puerpério"])

# --- 3. LÓGICA DE FILTRAGEM POR GRUPO ---

todos_ind_nomes = df_ind.columns[1:].tolist()

if grupo == "Infantil":
    # Indicadores: Colunas 1 a 5 | Classificação: Linhas 1 e 2
    lista_indicadores = todos_ind_nomes[0:5]
    df_cvat = df_class.iloc[1:3].copy()
else:
    # Indicadores: Colunas 6 em diante | Classificação: Linhas 6 e 7
    lista_indicadores = todos_ind_nomes[5:]
    df_cvat = df_class.iloc[6:8].copy()

# --- 5. SEÇÃO: MONITORAMENTO DE INDICADORES (ARQUIVO 1) ---

st.header("2. Detalhamento dos Indicadores")
selecionado = st.selectbox("Selecione o Indicador para análise detalhada:", lista_indicadores)

col_graf_ind, col_tab_ind = st.columns([4, 1])

with col_graf_ind:
    fig_linha = px.line(
        df_ind, x="Mês", y=selecionado, 
        markers=True, text=selecionado,
        title=f"Evolução: {selecionado}"
    )
    fig_linha.update_traces(textposition="top center")
    fig_linha.update_layout(margin=dict(t=80, b=40, l=40, r=40))
    st.plotly_chart(fig_linha, use_container_width=True, key="linha_ind")

with col_tab_ind:
    st.write("### Dados")
    st.dataframe(df_ind[["Mês", selecionado]], hide_index=True, use_container_width=True)

# Ajuste fino na tabela de classificação
df_cvat.columns = df_class.iloc[0].values
df_cvat.rename(columns={df_cvat.columns[0]: "Status"}, inplace=True)
meses_colunas = df_cvat.columns[1:13]

# --- 4. SEÇÃO: CLASSIFICAÇÃO CVAT (ARQUIVO 2) ---

st.title(f"📊 Dashboard APS - {grupo}")
st.header("1. Classificação CVAT")

col_pizza, col_barra_cvat = st.columns([1, 2])

with col_pizza:
    # Cálculo do Total para a Pizza
    df_cvat['Total'] = df_cvat[meses_colunas].apply(pd.to_numeric, errors='coerce').sum(axis=1)
    fig_pizza = px.pie(
        df_cvat, values='Total', names='Status', 
        title="Distribuição Anual",
        color='Status',
        color_discrete_map={'REGULAR': '#EF553B', 'SUFICIENTE': '#00CC96'},
        hole=0.4
    )
    st.plotly_chart(fig_pizza, use_container_width=True, key="pizza_cvat")

with col_barra_cvat:
    # Transformar para formato longo para o gráfico de barras
    df_melted = df_cvat.melt(id_vars=["Status"], value_vars=meses_colunas, var_name="Mês", value_name="Quantidade")
    fig_barra_cvat = px.bar(
        df_melted, x="Mês", y="Quantidade", color="Status",
        title="Evolução Mensal da Classificação",
        barmode="group",
        color_discrete_map={'REGULAR': '#EF553B', 'SUFICIENTE': '#00CC96'},
        text_auto=True
    )
    st.plotly_chart(fig_barra_cvat, use_container_width=True, key="barra_cvat")

st.divider()

# Gráfico de barras de indicadores (opcional, no final)
fig_barra_ind = px.bar(df_ind, x="Mês", y=selecionado, title="Comparativo Mensal", color_discrete_sequence=['#636EFA'])
st.plotly_chart(fig_barra_ind, use_container_width=True, key="barra_ind_final")
