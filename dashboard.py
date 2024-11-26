import streamlit as st
import pandas as pd
import plotly.express as px

# Carregar os dados de frequências de palavras-chave
freq_df = pd.read_csv('freq_df.csv')

file_path = 'blooms_taxonomy_dataset_pt_br.csv'
df = pd.read_csv(file_path)

# Configuração do Streamlit
st.set_page_config(
    page_title="Dashboard de Palavras-Chave",
    layout="wide",
)

# Título do Dashboard
st.title("Dashboard de Verbos por Nível da Taxonomia de Bloom")

# Sidebar para filtros
st.sidebar.header("Filtros")

# Definir o número mínimo de ocorrências para os verbos
min_occurencias = st.sidebar.number_input(
    "Número mínimo de ocorrências para um verbo aparecer no gráfico:",
    min_value=1,
    value=5,
    step=1,
    key="min_occurencias"  # Adicionando uma chave única
)

# Calcular a frequência total de cada verbo em todas as categorias
verbos_frequentes = freq_df.groupby('Keyword')['Frequency'].sum()

# Filtrar os verbos que atendem à condição de número mínimo de ocorrências
verbos_filtrados = verbos_frequentes[verbos_frequentes >= min_occurencias].index.tolist()

# Exibir o filtro para as categorias
categorias = st.sidebar.multiselect(
    "Selecione as Categorias:",
    options=freq_df["Categoria"].unique(),
    default=freq_df["Categoria"].unique(),
    key="categorias"  # Chave única para as categorias
)

# Exibir o filtro para os verbos (usando apenas os verbos filtrados)
keywords = st.sidebar.multiselect(
    "Selecione os Verbos (Palavras-Chave):",
    options=verbos_filtrados,
    default=verbos_filtrados,
    key="keywords"  # Chave única para os verbos
)

# Filtrar os dados com base nas escolhas do usuário
filtered_df = freq_df[
    (freq_df["Categoria"].isin(categorias)) &
    (freq_df["Keyword"].isin(keywords))
]

# Ordenar as categorias de forma explícita
categoria_order = sorted(filtered_df['Categoria'].unique())  # Ajuste se quiser uma ordem personalizada

# Garantir que as categorias estejam na ordem correta
filtered_df['Categoria'] = pd.Categorical(filtered_df['Categoria'], categories=categoria_order, ordered=True)

# Heatmap interativo
fig = px.density_heatmap(
    filtered_df,
    x="Keyword",
    y="Categoria",
    z="Frequency",
    color_continuous_scale='Viridis',
    title="Heatmap de Frequências por Nível da Taxonomia e Verbo",
)

# Layout do Heatmap
fig.update_layout(margin=dict(l=40, r=40, t=40, b=40))

# Mostrar o gráfico
st.plotly_chart(fig, use_container_width=True)
# Supondo que 'df' seja o DataFrame original que contém as questões
selected_keyword = st.selectbox(
    "Selecione um verbo para visualizar as questões:",
    options=verbos_filtrados,
    key="selected_keyword"
)

# Filtrar o DataFrame original 'df' para obter as questões relacionadas ao verbo selecionado
exemplos = df[df["Questões"].str.contains(selected_keyword, na=False)]

# Exibir as questões relacionadas ao verbo
st.subheader(f"Exemplos de questões com o verbo '{selected_keyword}'")

if not exemplos.empty:
    for _, row in exemplos.iterrows():
        st.write(f"**Categoria**: {row['Categoria']}")
        st.write(f"**Questão**: {row['Questões']}")  # Use a coluna original de 'Questões'
else:
    st.write("Não foram encontradas questões para esse verbo.")

