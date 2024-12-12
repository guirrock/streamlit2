import streamlit as st
import pandas as pd
import plotly.express as px

# Carregar os dados de frequências de palavras-chave
freq_df = pd.read_csv('freq_df.csv')

# Garantir que todas as categorias da Taxonomia de Bloom estão presentes
categorias_bloom = ["BT1", "BT2", "BT3", "BT4", "BT5", "BT6"]
freq_pivot = freq_df.pivot(index='Categoria', columns='Keyword', values='Frequency').reindex(categorias_bloom, fill_value=0)

# Título do Dashboard
st.title("Dashboard de Frequências de Verbos por Categoria da Taxonomia de Bloom")

# Selecionar a categoria de referência para ordenação
categoria_ref = st.selectbox(
    "Selecione a categoria da Taxonomia de Bloom para ordenar os verbos:",
    options=categorias_bloom,
    index=0
)

# Ordenar os verbos com base na categoria selecionada
freq_pivot = freq_pivot.sort_values(by=categoria_ref, axis=1, ascending=False)

# Criar o heatmap usando Plotly
heatmap = px.imshow(
    freq_pivot,
    labels={"x": "Verbos", "y": "Categorias", "color": "Frequência"},
    color_continuous_scale="Viridis",
)

# Configurar título e layout do heatmap
heatmap.update_layout(
    title="Heatmap de Frequências de Verbos por Categoria",
    xaxis_title="Verbos",
    yaxis_title="Categorias",
    xaxis=dict(tickangle=-45)  # Inclinar os rótulos dos verbos para melhor visualização
)

# Exibir o heatmap
st.plotly_chart(heatmap)

# Observação sobre a funcionalidade
st.markdown(
    "Selecione uma categoria de referência para reorganizar os verbos com base na frequência nessa categoria."
)
