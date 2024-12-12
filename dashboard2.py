import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import re

# Personalizando o fundo dos widgets e o layout usando CSS
st.markdown("""
    <style>
        /* Cor de fundo geral da aplicação */
        .reportview-container {
            background-color: #F0F7FF; /* Azul muito suave de fundo */
        }
        
        /* Cor de fundo do campo de seleção */
        .stSelectbox, .stNumberInput, .stSlider {
            background-color: #D9E8FF; /* Azul suave mais claro */
            border-radius: 8px;
        }

        /* Cor de fundo da barra de título */
        .css-18e3th9 {
            background-color: #1F76D2; /* Azul mais escuro para o título */
            color: white;
        }

        /* Alterando a cor de fundo da sidebar se necessário */
        .sidebar .sidebar-content {
            background-color: #1F76D2;
        }
        
        /* Ajustando o estilo da cor de fundo do botão */
        .stButton button {
            background-color: #1F76D2;
            color: white;
        }

        /* Melhorando a cor do texto das opções */
        .stSelectbox div[data-baseweb="select"] {
            color: #1F76D2;
        }
    </style>
""", unsafe_allow_html=True)

# Carregar os arquivos de dados
df = pd.read_csv("freq_df.csv")
perguntas_df = pd.read_csv("blooms_taxonomy_dataset_pt_br.csv")

# Criando uma tabela de contagem para cada verbo em cada categoria
pivot_df = df.pivot_table(index='Categoria', columns='Keyword', values='Frequency', aggfunc='sum', fill_value=0)

# Título do dashboard
st.title('Análise de Verbos por Nível da Taxonomia de Bloom')

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

# Opção para o usuário selecionar quais verbos exibir no heatmap
verbos_disponiveis = list(pivot_df_filtered.columns)
verbos_selecionados = st.multiselect('Escolha os verbos que deseja exibir no heatmap:', verbos_disponiveis, default=verbos_disponiveis)

# Filtra o dataframe com base nos verbos selecionados
pivot_df_filtered = pivot_df_filtered[verbos_selecionados]

# Criando o heatmap com Plotly
fig = go.Figure(data=go.Heatmap(
    z=pivot_df_filtered.values,  # Frequências
    x=pivot_df_filtered.columns,  # Verbos (colunas)
    y=pivot_df_filtered.index,  # Categorias (linhas)
    colorscale='Blues',  # Escala de cores
    hovertemplate=(
        'Verbo: %{x}<br>'  # Exibe o verbo no eixo X
        'Categoria: %{y}<br>'  # Exibe a categoria no eixo Y
        'Frequência: %{z}<br>'  # Exibe a frequência no eixo Z
        '<extra></extra>'  # Remove a legenda extra padrão do tooltip
    ),
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

# Selecione um verbo e categoria para exibir as perguntas
selected_verb = st.selectbox('Escolha um verbo:', verbos_selecionados)
selected_category = st.selectbox('Escolha uma categoria de Bloom:', categorias_ordenadas)

# Filtrar as perguntas que contêm o verbo selecionado (com str.contains) e a categoria de Bloom selecionada
perguntas_filtradas = perguntas_df[
    perguntas_df['Questões'].str.contains(r'\b' + selected_verb + r'\b', case=False, na=False)
    & perguntas_df['Categoria'].str.contains(selected_category)
]

# Exibir as perguntas filtradas
if not perguntas_filtradas.empty:
    st.subheader('Perguntas encontradas:')
    for index, row in perguntas_filtradas.iterrows():
        # Verificar se a 'Questões' não é NaN e é uma string
        if isinstance(row['Questões'], str):
            # Destacar o verbo na pergunta
            pergunta_destacada = re.sub(rf'\b{selected_verb}\b', f"<mark>{selected_verb}</mark>", row['Questões'], flags=re.IGNORECASE)
            st.markdown(f"- {pergunta_destacada}", unsafe_allow_html=True)
else:
    st.write("Nenhuma pergunta encontrada para o verbo e categoria selecionados.")
