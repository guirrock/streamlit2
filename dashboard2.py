import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Carregar o CSV
df = pd.read_csv("freq_df.csv")

# Criando uma tabela de contagem para cada verbo em cada categoria
pivot_df = df.pivot_table(index='Categoria', columns='Keyword', values='Frequency', aggfunc='sum', fill_value=0)

# Título do dashboard
st.title('Heatmap de Frequência de Verbos por Nível da Taxonomia de Bloom')

# Opção para o usuário escolher a categoria para ordenar os verbos no eixo X
categorias = df['Categoria'].unique()  # Obtém as categorias únicas no dataframe
categoria_selecionada = st.selectbox('Escolha a categoria para ordenar os verbos:', categorias)

# Ordenando os verbos na categoria selecionada
frequencias_categoria = df[df['Categoria'] == categoria_selecionada].groupby('Keyword')['Frequency'].sum().sort_values(ascending=False)

# Reordenando as colunas do heatmap com base nas frequências da categoria selecionada
pivot_df = pivot_df[frequencias_categoria.index]

# Criando o heatmap com Plotly
fig = go.Figure(data=go.Heatmap(
    z=pivot_df.values,  # Frequências
    x=pivot_df.columns,  # Verbos (colunas)
    y=pivot_df.index,  # Categorias (linhas)
    colorscale='Viridis',  # Escala de cores
))

# Adicionando título e rótulos ao gráfico
fig.update_layout(
    title=f'Heatmap de Frequência de Verbos por Nível da Taxonomia de Bloom (Ordenado por {categoria_selecionada})',
    xaxis_title='Verbos',
    yaxis_title='Categorias da Taxonomia de Bloom',
    xaxis={'tickangle': 45},  # Rotacionando os rótulos dos verbos para melhor visualização
    yaxis={'categoryorder': 'total ascending'}  # Ordenando as categorias
)

# Exibindo o gráfico no Streamlit
st.plotly_chart(fig)

