# -*- coding: utf-8 -*-
"""filmes_recomendacao.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1aVVpCw6hcjH80EQ_ZX-aCwBJo1qPioHB
"""

import pandas as pd

!pip install seaborn==0.9.0

"""Com o pandas importado, vamos buscar os dados dos filmes pela URI e renomear as colunas do Dataframe:"""

uri_filmes = 'https://raw.githubusercontent.com/fabriciobedin/machine-learning/master/movies_classification/movies.csv'
filmes = pd.read_csv(uri_filmes)

filmes.columns = ['filme_id', 'titulo', 'generos']
filmes.head()

"""Com isso, podemos extrair os dummies da coluna de gêneros. Logo, vamos falar para o nosso Dataframe de filmes pegar a coluna gêneros como string (str) e pegar os dummies (get_dummies):"""

generos = filmes.generos.str.get_dummies()

"""Isso retorna para gente um Dataframe com os dummies dos gêneros.

Podemos pegar este Dataframe e pedir para o pandas concatená-lo (concat) com o de filmes com as colunas (axis=1).
"""

dados_dos_filmes = pd.concat([filmes, generos], axis=1)
dados_dos_filmes.head()

"""Por fim, temos que reescalar os dummies para saber quais dos gêneros mais influenciam os filmes. Portanto vamos importar o escalador da biblioteca sklearn e criar um objeto a partir da classe StandardScaler:

Vamos falar para o scaler aprender com os dummies e transformá-los (fit_transform) para que, dessa forma, tenhamos mais informações sobre como os gêneros influenciam o filme:
"""

from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
generos_escalados = scaler.fit_transform(generos)
generos_escalados

"""Em primeiro lugar, temos que importar do módulo de cluster da sklearn o algoritmo do K-Means.

Após isso, podemos criar nosso objeto que representará o modelo KMeans. Para criar um objeto do K-Means, precisamos falar o número de clusters (n_clusters), isto é, quantos grupos diferentes serão agrupados. No caso, apenas para testar o algoritmo, vamos passar três como valor:
"""

from sklearn.cluster import KMeans
modelo = KMeans(n_clusters=3)

"""Em seguida, podemos falar para o K-Means agrupar os dados (generos_escalados) para a gente através do método fit:

Podemos ver os resultados do agrupamento imprimindo os rótulos (labels_) do modelo:
"""

modelo.fit(generos_escalados)
print(f'Grupos {modelo.labels_}')

"""Vamos começar visualizando os centróides de cada grupo. Para isso, podemos falar para o Python imprimir os centróides e os nomes dos gêneros - que são as colunas do data frame generos:"""

print(generos.columns)
print(modelo.cluster_centers_)

"""Para facilitar o trabalho e a manipulação desses dados, vamos criar um data frame chamado grupos a partir dos centróides.

Portanto, falamos para o pandas (pd) criar um DataFrame a partir dos centróides e nomear as colunas (columns) com o nome dos gêneros:
"""

grupos = pd.DataFrame(modelo.cluster_centers_, columns=generos.columns)

"""Podemos ver o data frame colocando a variável grupos como a última instrução da célula.

Vamos visualizar os centróides transpondo (transpose) o data frame de grupos e pedindo para o pandas plotar (plot) um gráfico de barras (bar). Como queremos que cada cluster tenha seu próprio gráfico, vamos falar que teremos subplots e para facilitar a visualização, vamos definir um tamanho para a figura (figsize) e dizer que não queremos compartilhar os labels do eixo x:
"""

grupos.transpose().plot.bar(subplots=True,
               figsize=(25, 25),
               sharex=False)

"""Podemos visualizar os filmes pertencentes a algum grupo, por exemplo o grupo 0. Basta realizar um filtro pelos labels_ do modelo e pedir alguns dados da amostra:"""

grupo = 0

filtro = modelo.labels_ == grupo

dados_dos_filmes[filtro].sample(10)

"""Vamos plotar um gráfico de pontos. Porém, temos 20 gêneros, ou seja, 20 dimensões. Logo, antes de plotar o gráfico, temos que reduzir as dimensões. Para isso, vamos utilizar o algoritmo TNSE do módulo manifold da sklearn."""

from sklearn.manifold import TSNE

"""A partir desse algoritmo podemos criar um objeto TSNE e utilizar o método fit_transform. Este método nos retorna um array do numpy com as features reduzidas."""

tsne = TSNE()

visualizacao = tsne.fit_transform(generos_escalados)

"""Agora basta importamos o seaborn e plotar um gráfico de dispersão (scatterplot).

Mas antes, vamos atribuir um valor para o tamanho da figura (figure.figsize), apenas para facilitar a visualização:
"""

import seaborn as sns

sns.set(rc={'figure.figsize': (13, 13)})



sns.scatterplot(x=visualizacao[:, 0],
               y=visualizacao[:, 1],
               hue=modelo.labels_,
               palette=sns.color_palette('Set1', 3))

"""Vamos tentar fazer um agrupamento um pouquinho diferente do primeiro. Neste caso, vamos criar um modelo K-Means e falar para ele agrupar os dados em 20 grupos (um para cada gênero). Com o modelo criado, vamos treiná-lo passando os generos_escalados:

Como antes, vamos criar um data frame a partir do centróides do grupo:

E plotar um gráfico para cada centróide. Dessa vez, vamos rotacionar (rot) os rótulos do eixo x para ficar mas legível:
"""

modelo = KMeans(n_clusters=20)

modelo.fit(generos_escalados)

grupos = pd.DataFrame(modelo.cluster_centers_,
            columns=generos.columns)

grupos.transpose().plot.bar(subplots=True,
               figsize=(25, 50),
               sharex=False,
               rot=0)

"""Como antes, vamos pegar algum grupo e fazer uma filtragem no data frame de filmes para ver como foram agrupados:"""

grupo = 2

filtro = modelo.labels_ == grupo

dados_dos_filmes[filtro].sample(10)

"""Aparentemente, os dados foram agrupados de uma maneira que faz sentido. Mas então, quantos grupos devemos usar?

Vamos criar a função que recebe o número de clusters e os dados e retorna o número de clusters e o erro (inertia_) daquele modelo:
"""

def kmeans(numero_de_clusters, generos):
  modelo = KMeans(n_clusters=numero_de_clusters)
  modelo.fit(generos)
  return [numero_de_clusters, modelo.inertia_]

kmeans(20, generos_escalados)

kmeans(3, generos_escalados)

"""Vamos rodar essa função começando a agrupar em um único grupo e ir agrupando até 40 grupos. Para isso, vamos usar uma compressão de lista do Python:"""

resultado = [kmeans(numero_de_grupos, generos_escalados) for numero_de_grupos in range(1, 41)]
resultado

"""Para facilitar o trabalho, vamos transformar essa variável em um data frame para facilitar sua manipulação:"""

resultado = pd.DataFrame(resultado, 
            columns=['grupos', 'inertia'])
resultado

"""Agora, basta plotarmos um gráfico da coluna inertia do data frame. Lembrando que devemos passar a coluna grupos como parâmetro dos rótulos do eixo x:"""

resultado.inertia.plot(xticks=resultado.grupos)

"""Podemos ver que o ponto de quebra no gráfico foi próximo ao número 17, logo, esse é o número de clusters que otimiza nosso modelo. Podemos rodar um novo modelo com 17 grupos e mostrar seus centróides:"""

modelo = KMeans(n_clusters=17)
modelo.fit(generos_escalados)

grupos = pd.DataFrame(modelo.cluster_centers_,
            columns=generos.columns)

grupos.transpose().plot.bar(subplots=True,
               figsize=(25, 50),
               sharex=False,
               rot=0)

"""Podemos também realizar um filtro por algum grupo para ver se fazem sentido:"""

grupo = 16

filtro = modelo.labels_ == grupo

dados_dos_filmes[filtro].sample(10)

"""Vamos começar importando o algoritmo AgglomerativeClustering da biblioteca sklearn:"""

from sklearn.cluster import AgglomerativeClustering

"""Algoritmo importado, vamos criar um modelo e, seguindo o K-Means, vamos falar que queremos agrupar em 17 grupos. Modelo criado, basta falar para ele aprender e retornar os grupos (fit_predict):"""

modelo = AgglomerativeClustering(n_clusters=17)
grupos = modelo.fit_predict(generos_escalados)
grupos

"""Vamos rodar o algoritmo TSNE para visualizar os dados. Para isso, vamos utilizar a mesma abordagem que utilizamos anteriormente. Criar um objeto a partir da classe e pedir para ele transformar nossos gêneros:"""

tsne = TSNE()
visualizacao = tsne.fit_transform(generos_escalados)
visualizacao

"""Bacana! Agora, basta plotar com um gráfico de dispersão passando como parâmetro de cores os grupos criados pelo AgglomerativeClustering:"""

sns.scatterplot(x=visualizacao[:, 0],
               y=visualizacao[:, 1],
               hue=grupos)

"""Porém, quando utilizamos o agrupamento hierárquico, uma forma comum de visualização é através do dendrograma. Para plotar o dendrograma, precisamos da matriz de distâncias dos dados e da função que plota o dendrograma propriamente dito. Vamos importá-las da biblioteca scipy:"""

from scipy.cluster.hierarchy import dendrogram, linkage

"""Antes de plotar o dendrograma, vamos agrupar novamente os dados com o K-Means para ter uma visualização dos centróides mais próxima a célula do dendrograma (e para sobrescrever as variáveis que usamos com o mesmo nome):"""

modelo = KMeans(n_clusters=17)
modelo.fit(generos_escalados)

grupos = pd.DataFrame(modelo.cluster_centers_,
            columns=generos.columns)

grupos.transpose().plot.bar(subplots=True,
               figsize=(25, 50),
               sharex=False,
               rot=0)

"""Agora, basta criarmos a matriz de distâncias baseada nos grupos do K-Means e plotar o dendrograma:"""

matriz_de_distancia = linkage(grupos)
matriz_de_distancia

dendrograma = dendrogram(matriz_de_distancia)

