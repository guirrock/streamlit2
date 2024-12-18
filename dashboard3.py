import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import re
import networkx as nx
from pyvis.network import Network
from nltk.tokenize import word_tokenize
from collections import Counter
import re

import nltk
nltk.download('punkt')

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
    st.subheader(f"Perguntas filtradas para '{selected_verb}' em '{selected_category}':")

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






st.subheader('Criar Árvore de Palavras com o Verbo Selecionado')

# Filtrar as perguntas com base no verbo selecionado
selected_verb = st.selectbox('Escolha um verbo para a árvore:', verbos_selecionados)

# Filtrar o dataset para as perguntas que contêm o verbo selecionado
filtered_questions = perguntas_df[perguntas_df['Questões'].str.contains(rf'\b{selected_verb}\b', case=False, na=False)]

if not filtered_questions.empty:
    st.subheader(f"Gerando árvore para o verbo '{selected_verb}':")

    # Tokenizar as perguntas e extrair palavras subsequentes ao verbo
    word_sequences = []
    for question in filtered_questions['Questões']:
        if isinstance(question, str):
            tokens = word_tokenize(question.lower())  # Tokenizar a frase
            try:
                verb_index = tokens.index(selected_verb.lower())  # Encontra o índice do verbo
                word_sequences.append(tokens[verb_index + 1:])  # Pega palavras após o verbo
            except ValueError:
                continue  # Ignora se o verbo não está presente

    # Contar as palavras mais frequentes em cada nível da árvore
    tree_structure = {selected_verb: {}}  # Raiz da árvore é o verbo
    current_level = {selected_verb: word_sequences}  # Começa com o verbo e as palavras subsequentes

    # Número de níveis e palavras por nível
    num_levels = 3
    num_words_per_level = 2

    for level in range(num_levels):
        next_level = {}
        for node, sequences in current_level.items():
            # Conta as palavras que aparecem após o nó atual
            word_counter = Counter(word for seq in sequences for word in seq[:1])  # Apenas a próxima palavra
            most_common_words = word_counter.most_common(num_words_per_level)

            # Adiciona as palavras mais comuns ao próximo nível
            tree_structure[node] = {}
            for word, _ in most_common_words:
                # Filtra as sequências para as palavras que começam com a palavra atual
                filtered_sequences = [seq[1:] for seq in sequences if seq and seq[0] == word]
                tree_structure[node][word] = {}
                next_level[word] = filtered_sequences

        current_level = next_level  # Atualiza o nível atual

    # Criar a árvore com NetworkX
    graph = nx.DiGraph()
    def add_edges(tree, parent=None):
        for node, children in tree.items():
            if parent:
                graph.add_edge(parent, node)  # Adiciona aresta entre nós
            add_edges(children, node)

    add_edges(tree_structure)

    # Visualizar a árvore com PyVis
    net = Network(notebook=True, height="600px", width="100%", directed=True)
    net.from_nx(graph)
    net.show("tree.html")

    # Exibir a árvore interativa no Streamlit
    st.components.v1.html(open("tree.html", "r").read(), height=650, scrolling=True)
else:
    st.write(f"Nenhuma pergunta encontrada para o verbo '{selected_verb}'.")

