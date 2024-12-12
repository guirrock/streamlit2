import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Carregar o CSV
df = pd.read_csv("freq_df.csv", delimiter="\t")

# Criando uma tabela de contagem para cada verbo em cada categoria
pivot_df = df.pivot_table(index='Categoria', columns='Keyword', values='Frequency', aggfunc='sum', fill_value=0)

# Título do dashboard
st.title('Heatmap de Frequência de Verbos por Nível da Taxonomia de Bloom')

# Criando o heatmap com Plotly
fig = go.Figure(data=go.Heatmap(
    z=pivot_df.values,  # Frequências
    x=pivot_df.columns,  # Verbos (colunas)
    y=pivot_df.index,  # Categorias (linhas)
    colorscale='Viridis',  # Escala de cores
))

# Adicionando título e rótulos ao gráfico
fig.update_layout(
    title='Heatmap de Frequência de Verbos por Nível da Taxonomia de Bloom',
    xaxis_title='Verbos',
    yaxis_title='Categorias da Taxonomia de Bloom',
    xaxis={'tickangle': 45},  # Rotacionando os rótulos dos verbos para melhor visualização
    yaxis={'categoryorder': 'total ascending'}  # Ordenando as categorias
)

# Exibindo o gráfico no Streamlit
st.plotly_chart(fig)

