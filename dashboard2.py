import streamlit as st
import pandas as pd
import plotly.express as px

# Título do app
st.title("Análise de Verbos por Categorias da Taxonomia de Bloom")

# Carregar os dados de frequências de palavras-chave
freq_df = pd.read_csv('freq_df.csv')

# Exibir os dados carregados
st.write("Dados carregados:", freq_df.head())

# Seleção da categoria de referência
categorias = freq_df['Categoria'].unique()
categoria_ref = st.selectbox("Escolha a categoria de referência para ordenar os verbos:", categorias)

# Pivotar os dados para o formato de heatmap
heatmap_data = freq_df.pivot_table(index='Categoria', columns='Keyword', values='Frequency', fill_value=0)

# Reordenar as colunas com base na categoria de referência
if categoria_ref in heatmap_data.index:
    colunas_ordenadas = heatmap_data.loc[categoria_ref].sort_values(ascending=False).index
    heatmap_data = heatmap_data[colunas_ordenadas]

# Garantir que todas as categorias sejam exibidas no eixo Y
heatmap_data = heatmap_data.reindex(index=categorias)

# Plotar o heatmap com Plotly
st.write(f"Heatmap com ordenação baseada na categoria: {categoria_ref}")
fig = px.imshow(heatmap_data, 
                labels=dict(x="Verbos", y="Categorias", color="Frequência"),
                x=heatmap_data.columns,
                y=heatmap_data.index,
                color_continuous_scale="YlGnBu")
st.plotly_chart(fig)
