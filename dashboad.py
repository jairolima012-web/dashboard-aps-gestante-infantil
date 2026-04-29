import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(layout="wide", page_title="Dashboard APS Indicadores")

# 1. Carregamento dos dados
df = pd.read_csv("Consolidado_G_I.csv", skiprows=1, encoding="latin1")
df.rename(columns={df.columns[0]: "Mês"}, inplace=True)
df.columns = df.columns.str.strip()

# 2. Filtros na Sidebar
st.sidebar.header("Filtros")
todos_indicadores = df.columns[1:].tolist()

# Seletor de Grupo
selecionado_grupo = st.sidebar.radio("Filtrar por Grupo:", ["Infantil", "Gestação e Puerpério"])

# Lógica de fatiamento das colunas (Infantil: primeiras 5 / Gestação: restante)
if selecionado_grupo == "Infantil":
    indicadores_filtrados = todos_indicadores[0:5]
else:
    indicadores_filtrados = todos_indicadores[5:]

# Seletor de Indicador
selecionado = st.sidebar.selectbox("Selecione o Indicador:", indicadores_filtrados)

# 3. Título Principal
st.title(f"📈 Monitoramento: {selecionado_grupo}")
st.markdown(f"**Indicador:** {selecionado}")

# 4. Layout com Proporção 4 para 1 (Gráfico grande, Tabela pequena)
col_grafico, col_tabela = st.columns([4, 1])

with col_grafico:
    fig_linha = px.line(
        df, 
        x="Mês", 
        y=selecionado, 
        markers=True,
        text=selecionado,
        title="Evolução Mensal"
    )
    fig_linha.update_traces(textposition="top center")
    
    # ADICIONADO 'key' PARA EVITAR O ERRO DE DUPLICIDADE
    st.plotly_chart(fig_linha, use_container_width=True, key="grafico_linha_principal")

with col_tabela:
    st.write("### Dados")
    st.dataframe(
        df[["Mês", selecionado]], 
        use_container_width=True, 
        hide_index=True
    )

# 5. Segundo Gráfico (Barras) na parte inferior
st.divider()
fig_barra = px.bar(
    df, 
    x="Mês", 
    y=selecionado,
    color=selecionado,
    color_continuous_scale="Blues",
    title="Comparativo entre Meses"
)

# ADICIONADO 'key' DIFERENTE AQUI TAMBÉM
st.plotly_chart(fig_barra, use_container_width=True, key="grafico_barra_comparativo")