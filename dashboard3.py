import pandas as pd
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import streamlit as st
import re
import networkx as nx
from pyvis.network import Network
from nltk.tokenize import word_tokenize
from collections import Counter
import re
from collections import defaultdict
import wordtree
import graphviz
from io import BytesIO
import base64
import random
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator



st.set_page_config(
    layout="wide",  # Define o layout para usar a largura total
)

# Título do dashboard
st.markdown("<h1 style='text-align: center; color: red;'>Visualizador de Questões Avaliativas Geradas (VisAQG)</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: black;'>Projeto Final - Disciplina - Visual Analytics for Data Science - INF/UFRGS</h3>", unsafe_allow_html=True)

# Adicionar estilo CSS para a área de rolagem fixa
st.markdown(
    """
    <style>
    .scrollable-box {
        max-height: 300px; /* Altura fixa para a área */
        overflow-y: auto; /* Adicionar barra de rolagem */
        padding: 10px;
        border: 1px solid #ccc;
        border-radius: 5px;
        background-color: #f9f9f9;
        font-family: Arial, sans-serif;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Carregar os arquivos de dados
df = pd.read_csv("freq_df.csv")
perguntas_df = pd.read_csv("blooms_taxonomy_dataset_pt_br.csv")

# Criando uma tabela de contagem para cada verbo em cada categoria
pivot_df = df.pivot_table(index='Categoria', columns='Keyword', values='Frequency', aggfunc='sum', fill_value=0)

# Opção para o usuário escolher a categoria para ordenar os verbos no eixo X
categorias = df['Categoria'].unique()  # Obtém as categorias únicas no dataframe
categoria_selecionada = st.selectbox('Escolha a categoria para ordenar os verbos no heatmap:', categorias)

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
    colorscale='Reds',  # Escala de cores
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
    margin=dict(l=40, r=40, t=80, b=150),
)

# Adicionando legenda abaixo do gráfico com mais distância
fig.add_annotation(
    xref="paper", yref="paper",
    x=0.5, y=-0.60,  # Reposiciona mais abaixo (-0.35)
    text=(
        "BT1 - Lembrar | BT2 - Compreender | BT3 - Aplicar | "
        "BT4 - Analisar | BT5 - Avaliar | BT6 - Criar"
    ),
    showarrow=False,
    font=dict(size=12),
    xanchor="center",
)

# Exibindo o gráfico no Streamlit
st.plotly_chart(fig)

# Adicionar estilo CSS para a área de rolagem fixa
st.markdown(
    """
    <style>
    .scrollable-box {
        max-height: 300px; /* Altura fixa para a área */
        overflow-y: auto; /* Adicionar barra de rolagem */
        padding: 10px;
        border: 1px solid #ccc;
        border-radius: 5px;
        background-color: #f9f9f9;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.subheader('Filtrar perguntas por Verbo e Nível:')

# Selecione um verbo e categoria para exibir as perguntas
selected_verb = st.selectbox('Escolha um verbo:', verbos_selecionados)
selected_category = st.selectbox('Escolha uma categoria de Bloom:', categorias_ordenadas)

# Filtrar o dataset de verbos com base no verbo e na categoria selecionados
filtered_verbos = df[
    (df['Keyword'] == selected_verb) & (df['Categoria'] == selected_category)
]

# Obter os IDs das perguntas que contêm o verbo na categoria selecionada
if not filtered_verbos.empty:
    question_ids = []
    for ids in filtered_verbos['IDs_perguntas']:
        question_ids.extend(map(int, ids.split('/')))  # Coletar todos os IDs das perguntas

    # Filtrar as perguntas no DataFrame principal usando os IDs
    perguntas_filtradas = perguntas_df[perguntas_df['id_pergunta'].isin(question_ids)]
else:
    perguntas_filtradas = pd.DataFrame()

# Prefixo da palavra a ser destacada
prefix = re.escape(selected_verb[:4])

# Exibir as perguntas filtradas em uma área com barra de rolagem
if not perguntas_filtradas.empty:
    st.markdown(f"Perguntas filtradas para '{selected_verb}' em '{selected_category}':")

    # Construir um bloco único de HTML para todas as perguntas
    perguntas_html = '<div class="scrollable-box">'
    for index, row in perguntas_filtradas.iterrows():
        if isinstance(row['Questões'], str):
            # Destacar o verbo na pergunta
            pergunta_destacada = re.sub(
                rf'\b{prefix}[a-zA-Z]*\b',
                lambda match: f"<mark>{match.group()}</mark>",
                row['Questões'],
                flags=re.IGNORECASE
            )
            perguntas_html += f"<p>- {pergunta_destacada}</p>"
    perguntas_html += '</div>'

    # Renderizar as perguntas dentro da área de rolagem
    st.markdown(perguntas_html, unsafe_allow_html=True)
else:
    st.write(f"Nenhuma pergunta encontrada para o verbo '{selected_verb}' e categoria '{selected_category}'.")

st.markdown("</br>", unsafe_allow_html=True)
st.subheader(f"Árvore de Palavras do Verbo '{selected_verb}':")

coluna = 'Questões'

# Criar a lista 'documents' com os textos da coluna
documents = perguntas_df[coluna].tolist()

g = wordtree.search_and_draw(corpus = documents, keyword = selected_verb)

# Renderiza o grafo no Streamlit usando Graphviz
try:
    # Supondo que 'g' seja o gráfico gerado
    st.graphviz_chart(g)

except Exception as e:
    # Se ocorrer algum erro, exibimos uma mensagem de erro no Streamlit
    st.error(f"Ocorreu um erro ao tentar renderizar o gráfico: {e}")

st.markdown("</br>", unsafe_allow_html=True)
st.subheader(f"Núvem de Palavras para a categoria '{selected_category}' e Verbo '{selected_verb}':")

all_summary = " ".join(s for s in perguntas_df[perguntas_df['Categoria'] == selected_category]['Questões'])
# lista de stopword
stopwords = set(STOPWORDS)
stopwords.update([
    "é","a", "o", "as", "os", "à", "aos", "aquela", "aquelas", "aquelas", "aqueles", "aqui", "com", "como", "contra", "da", "das", "de", "delas", "dele", 
    "deles", "demais", "depois", "desde", "desta", "deste", "disso", "do", "dos", "e", "ela", "elas", "ele", "eles", "em", "então", "entre", "era", 
    "essas", "esses", "esta", "está", "estão", "estes", "estive", "estivemos", "estou", "eu", "essa", "essas", "este", "estes", "na", "nas", "no", 
    "nos", "não", "nós", "o", "os", "ou", "para", "pela", "pelas", "pelo", "pelos", "perante", "por", "porém", "que", "quando", "quanto", "quem", 
    "se", "seja", "sem", "sendo", "sob", "sobre", "sua", "suas", "seu", "seus", "só", "sob", "tanta", "tantas", "tanto", "tantos", "te", "tem", 
    "temos", "tendo", "tão", "teu", "teus", "ti", "todas", "todos", "tua", "tuas", "tudo", "uma", "umas", "um", "uns", "vai", "vamos", "você", 
    "vocês", "ainda", "alguém", "alguma", "algumas", "algum", "alguns", "isso", "essa", "essas", "essas", "estes", "isto", "mas", "mais", "menos", 
    "mim", "naquele", "naqueles", "nela", "neles", "não", "nem", "nem", "nosso", "nossos", "nossa", "nossas", "o", "os", "ou", "para", "pela", "pelas"
])

# gerar uma wordcloud
wordcloud = WordCloud(stopwords=stopwords,
                      background_color="black",
                      width=1600, height=800).generate(all_summary)
# Exibir a imagem no Streamlit
st.image(wordcloud.to_image(), use_container_width=True)
