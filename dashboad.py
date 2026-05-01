import streamlit as st
import pandas as pd
import plotly.express as px
import textwrap

st.set_page_config(layout="wide", page_title="Dashboard APS Integrado")

# --- CARREGAMENTO DOS DADOS ---

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

# --- SIDEBAR / FILTROS ---

st.sidebar.header("Configurações Gerais")
grupo = st.sidebar.radio("Selecione o Grupo de Análise:", ["Infantil", "Gestação e Puerpério"])

# --- LÓGICA DE FILTRAGEM POR GRUPO ---

todos_ind_nomes = df_ind.columns[1:].tolist()

if grupo == "Infantil":
    lista_indicadores = todos_ind_nomes[0:5]
    df_cvat = df_class.iloc[1:3].copy()
else:
    lista_indicadores = todos_ind_nomes[5:]
    df_cvat = df_class.iloc[6:8].copy()

st.header(f"📊 1. Detalhamento dos Indicadores")
selecionado = st.selectbox("Selecione o Indicador para análise detalhada:", lista_indicadores)

# --- INDICADORES tabela e gráfico

col_tab_ind, col_graf_ind = st.columns([2, 6])

with col_tab_ind:
    st.write("### Dados")

    meio = len(selecionado) // 2
    try:
        espaco_proximo = selecionado.find(" ", meio)
        if espaco_proximo == -1:
            espaco_proximo = selecionado.rfind(" ", 0, meio)
            
        if espaco_proximo != -1:
            coluna_visual = selecionado[:espaco_proximo] + "  \n" + selecionado[espaco_proximo+1:]
        else:
            coluna_visual = selecionado
    except:
        coluna_visual = selecionado

    st.dataframe(
        df_ind[["Mês", selecionado]],
        hide_index=True, 
        use_container_width=True,
        column_config={
            selecionado: st.column_config.Column(
                label=coluna_visual,
                width="large",
                help=f"Indicador completo: {selecionado}"
            ),
            "Mês": st.column_config.Column(width="small")
        }       
    )

with col_graf_ind:

    eixo_y = "<br>".join(textwrap.wrap(selecionado, width=50)) 
    
    fig_linha = px.line(
        df_ind, x="Mês", y=selecionado, 
        markers=True, text=selecionado,
        title=f"Evolução: {selecionado}"
    )
    
    fig_linha.update_traces(textposition="top center")

    fig_linha.update_layout(
        title={
            'text': f"Evolução: {selecionado}",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        yaxis_title=eixo_y,
        margin=dict(t=80, b=40, l=150, r=40)
    )

    st.plotly_chart(fig_linha, use_container_width=True, key="linha_ind")

# Gráfico de barras de indicadores
with col_graf_ind:

    eixo_y_barras = "<br>".join(textwrap.wrap(selecionado, width=50)) 
    
    # gráfico de barras
    fig_barra = px.bar(
        df_ind, 
        x="Mês", 
        y=selecionado, 
        text=selecionado,
        title=f"Evolução (Barras): {selecionado}"
    )
    
    fig_barra.update_traces(textposition="outside")

    fig_barra.update_layout(
        title={
            'text': f"Evolução: {selecionado}",
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        yaxis_title=eixo_y_barras,
        margin=dict(t=80, b=40, l=50, r=40),
        xaxis_title="Mês"
    )

    # Exibe o gráfico
    st.plotly_chart(fig_barra, use_container_width=True, key="barra_ind")

# Ajuste fino na tabela de classificação
df_cvat.columns = df_class.iloc[0].values
df_cvat.rename(columns={df_cvat.columns[0]: "Status"}, inplace=True)
meses_colunas = df_cvat.columns[1:13]

# CLASSIFICAÇÃO CVAT (ARQUIVO 2) ---

st.title(f"📊 2. Classificação CVAT")

col_pizza, col_barra_cvat = st.columns([1, 2])

with col_pizza:
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
