import streamlit as st
import pandas as pd
import plotly.express as px

# Carregar os dados de frequências de palavras-chave
freq_df = pd.read_csv('freq_df.csv')

# Título do Dashboard
st.title("Dashboard de Frequências de Verbos por Categoria da Taxonomia de Bloom")

# Selecionar a categoria de referência para ordenação
categoria_ref = st.selectbox(
    "Selecione a categoria da Taxonomia de Bloom para ordenar os verbos:",
    options=freq_df.columns[1:],  # Supondo que a primeira coluna seja 'Verbos'
    index=0
)

# Ordenar os dados com base na categoria selecionada
freq_df = freq_df.sort_values(by=categoria_ref, ascending=False)

# Criar o heatmap usando Plotly
heatmap = px.imshow(
    freq_df.iloc[:, 1:].T,  # Transpor para ter categorias no eixo Y e verbos no eixo X
    labels={"x": "Verbos", "y": "Categorias", "color": "Frequência"},
    x=freq_df['Verbos'],
    y=freq_df.columns[1:],
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
