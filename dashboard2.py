import pandas as pd
import streamlit as st
import plotly.express as px

# Carregar o arquivo CSV
file_path = 'freq_df.csv'  # Substituir pelo caminho real do arquivo se necessário
freq_df = pd.read_csv(file_path)

# Função para criar o DataFrame pivotado para o heatmap
def prepare_heatmap_data(df, sort_by):
    # Pivotar os dados
    pivot_df = df.pivot(index='Categoria', columns='Keyword', values='Frequency').fillna(0)

    # Garantir que todas as categorias sejam preservadas no índice
    pivot_df = pivot_df.reindex(df['Categoria'].unique(), fill_value=0)

    # Reordenar as colunas com base na categoria selecionada
    if sort_by in pivot_df.index:
        pivot_df = pivot_df.loc[:, pivot_df.loc[sort_by].sort_values(ascending=False).index]

    return pivot_df

# Configurar o Streamlit
st.title("Heatmap de Verbos por Categoria da Taxonomia de Bloom")

# Opção para selecionar a categoria de referência
categories = freq_df['Categoria'].unique()
sort_by = st.selectbox("Selecione a categoria para ordenar os verbos:", categories)

# Preparar os dados para o heatmap
heatmap_data = prepare_heatmap_data(freq_df, sort_by)

# Criar o heatmap com Plotly
fig = px.imshow(
    heatmap_data,
    labels={"x": "Verbos", "y": "Categorias", "color": "Frequência"},
    color_continuous_scale="Viridis",
    title=f"Heatmap de Frequências Ordenado por {sort_by}",
)

# Ajustar o layout para melhorar a legibilidade

fig.update_layout(
    xaxis=dict(title="Verbos", tickangle=-45),
    yaxis=dict(title="Categorias"),
    coloraxis_colorbar=dict(title="Frequência"),
    height=600  # Ajustar a altura do gráfico
)
fig.update_layout(margin=dict(l=40, r=40, t=40, b=40))
# Exibir o heatmap no Streamlit
st.plotly_chart(fig)

# Informar sobre os dados
st.write("Dados usados para o heatmap:")
st.dataframe(freq_df)
