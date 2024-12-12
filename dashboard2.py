import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# Carregar o CSV
df = pd.read_csv("freq_df.csv")

# Criando uma tabela de contagem para cada verbo em cada categoria
pivot_df = df.pivot_table(index='Categoria', columns='Keyword', values='Frequency', aggfunc='sum', fill_value=0)

# Título do dashboard
st.title('Frequência de Verbos por Nível da Taxonomia de Bloom')

# Opção para o usuário escolher a categoria para ordenar os verbos no eixo X
categorias = df['Categoria'].unique()  # Obtém as categorias únicas no dataframe
categoria_selecionada = st.selectbox('Escolha a categoria para ordenar os verbos:', categorias)

# Opção para o usuário inserir o número mínimo de vezes que cada verbo deve aparecer
min_freq = st.number_input('Número mínimo de aparições dos verbos no heatmap:', min_value=1, value=1, step=1)

# Filtrando os verbos com base na frequência mínima
df_filtered = df.groupby('Keyword').filter(lambda x: x['Frequency'].sum() >= min_freq)

# Criando uma nova tabela de contagem para os verbos filtrados
pivot_df_filtered = df_filtered.pivot_table(index='Categoria', columns='Keyword', values='Frequency', aggfunc='sum', fill_value=0)

# Ordenando os verbos na categoria selecionada
frequencias_categoria = df_filtered[df_filtered['Categoria'] == categoria_selecionada].groupby('Keyword')['Frequency'].sum().sort_values(ascending=False)

# Reordenando as colunas do heatmap com base nas frequências da categoria selecionada
pivot_df_filtered = pivot_df_filtered[frequencias_categoria.index]

# Garantindo que todas as categorias da Taxonomia de Bloom sejam exibidas
categorias_ordenadas = ['BT1', 'BT2', 'BT3', 'BT4', 'BT5', 'BT6']  # Ordem desejada das categorias

# Se a categoria não estiver presente, adicioná-la com zeros
pivot_df_filtered = pivot_df_filtered.reindex(categorias_ordenadas, axis=0, fill_value=0)

# Criando o heatmap com Plotly
fig = go.Figure(data=go.Heatmap(
    z=pivot_df_filtered.values,  # Frequências
    x=pivot_df_filtered.columns,  # Verbos (colunas)
    y=pivot_df_filtered.index,  # Categorias (linhas)
    colorscale='Viridis',  # Escala de cores
))

# Adicionando título e rótulos ao gráfico
fig.update_layout(
    title=f'Frequência de Verbos por Nível da Taxonomia de Bloom (Ordenado por {categoria_selecionada} e mínimo {min_freq} aparições)',
    xaxis_title='Verbos',
    yaxis_title='Categorias da Taxonomia de Bloom',
    xaxis={'tickangle': 45},  # Rotacionando os rótulos dos verbos para melhor visualização
    yaxis={'categoryorder': 'array', 'categoryarray': categorias_ordenadas},  # Garantindo a ordem das categorias
)

# Exibindo o gráfico no Streamlit
st.plotly_chart(fig)
