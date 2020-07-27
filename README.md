# Back end

Esse repositório contém os scripts em Python que alimentam o aplicativo. 

Na prática, assim que o usuário informa sua localização, a API do site chama os métodos que estão no diretório `code` para obter os dados necessários para a visualização de dados.

Os dados usados vêm do Censo de 2010 IBGE e do [Brasil.io](https://brasil.io). 

## Limitações

É importante frisar que o raio populacional exibido é referente ao total de habitantes da região do usuário na época de realização do último Censo, há cerca de dez anos. Esses são os dados mais recentes possíveis para esse nível de detalhamento.

Além disso, o cálculo parte do pressuposto que a população é distribuída homogeneamente dentro de cada setor censitário, o que não é necessariamente verdade, especialmente para blocos de maior área.

## Replicação passo-a-passo

Para reproduzir os resultados em sua própria máquina, você precisa configurar seu ambiente de desenvolvimento da seguinte maneira:

1. Clone o repositório

2. Baixe [este arquivo](https://drive.google.com/file/d/1Qr4R7Cv5xl949IAjGA-78MjAgni9BNSa/view?usp=sharing) compactado e extraia no diretório `data`.

3. Instale os requerimentos em um ambiente virtual do Anaconda com os seguinte comandos:

```
conda create -n gpd_0.8
conda activate gpd_0.8
conda config --env --add channels conda-forge
conda config --env --set channel_priority strict
conda install python=3 geopandas
conda install pygeos --channel conda-forge
conda install feather-format
conda install requests
```

Ou, caso prefira isntalar com outro método, veja a sessão [Using the optional PyGEOS dependency](https://geopandas.org/install.html#using-the-optional-pygeos-dependency) da documentação do GeoPandas.

4. Caso queira gerar também os pontos que aparecem no mapa, execute ```python generate_points.py```. Isso deve demorar um bocado e é opcional.

5. Use ```python prepare.py``` para pré-processar diversos dados, o que vai otimizar o processo de cálculo.

6. Use ```python run_query.py lat lon``` para obter um objeto JSON-like com as informações necessárias para gerar a visualização de dados personalizada.

7. O arquivo ```update.py``` deve ser executado repetidamente em um intervalo fixo de tempo via cron ou mecanismo semelhante. Ele é responsável por atualizar a contagem de casos de covid-19 no país, além de já calcular previamente o raio de mortes nas principais cidades do país.

Tenha em mente que o aplicativo roda em um ambiente Anaconda, criado exatamente seguindo as especificações desse tutorial, em um servidor Ubuntu 18.04. Não fizemos testes em outras configurações, mas sinta-se a vontade para abrir um issue caso encontre algum problema.

## Estrutura do repositório

### Diretório `code`

Esse diretório contém os scripts que processam os dados necessários para o funcionamento.

- **app.py**: implementa a API do aplicativo usando o framework [Flask](https://flask.palletsprojects.com/en/1.1.x/)

- **generate_points.py**: gera um arquivo no formato geojson com (aproximadamente) um ponto para cada habitante do país. O cálculo é feito gerando pontos de forma aleatória em um bounding box que envolve cada setor censitário. Ao fim do processo, removemos os pontos que foram gerados fora do setor. Para minimzar estes erros, estimamos a razão entre as áreas do bounding box e a área do setor e geramos pontos suficientes para compensar aqueles que ficaram fora dos limites. Usamos essa estratégia porque gerar apenas pontos que estejam garantidamente dentro do setor censitário, um polígono complexo, é computacionalmente dispendioso.

- **prepare.py**: script que encapsula as funções abaixo, que servem para pré-processar os dados necessários para execução dos cálculos

- **prepare_capitals_radius.py**: calcula o raio de mortes a partir de locais turísticos de dez capitais brasileiras e salva em um arquivo JSON. O método de cálculo é o mesmo utilizado no arquivo `run_query.py`.

- **prepare_city_bboxes.py**: divide o mapa do Brasil em 400 bounding boxes que contém os limites dos municípios e salva o resultado em arquivos no formato *feather*. Esse pré-processamento é necessário para melhorar o tempo de execução da função do arquivo `run_query.py` que encontra a cidade mais próxima ao usuário.

- **prepate_city_centroids.py**: salva os centróides das cidades do país em um arquivo no formato *feather*, otimizado para melhorar o tempo de leitura.

- **prepare_covid_count.py**: envia uma requisição para os servidores do Brasil.io e processa a resposta, salvando um arquivo JSON com dados sobre a quantidade de mortes por Covid 19 no país.

- **prepare_tracts_bboxes.py**: Usa o mesmo método do arquivo `prepare_city_bboxes.py` para dividir os setores censitários do Brasil em cerca de 10 mil arquivos diferentes, otimizando o tempo de carregamento.

- **run_query.py**: arquivo que gera os dados que são exibidos para o usuário do aplicativo: o raio de mortes ao redor da localização, a cidade mais próxima que desapareceria e o raio de mortes ao redor do centro de duas capitais. Descrevemos em mais detalhes como a computação funciona na sessão **Metodologia detalhada**, logo abaixo.

- **update.py**: script que encapsula as funções de e `prepare_capitals_radius.py` e `prepare_covid_count.py`, de forma a atualizar periodicamente os dados estáticos do alicativo.

### Diretório `data`

Contém informações sobre a divisão do país em setores censitários. Esses arquivos serão pré-processados para permitir que a execução aconteça de forma mais rápida.

## Metodologia detalhada

O algoritmo que calcula as informações exibidas para o usuário foi implementado no arquivo `run_query.py`. Confira abaixo uma descrição passo-a-passo do processo:

1. Ao receber o input do usuário, o script transforma as coordenadas em [objeto Point do Shapely](https://shapely.readthedocs.io/en/latest/manual.html#points).

```
point = parse_input(point)
```

2. O programa acessa o arquivo JSON gerado por `prepare_covid_count.py` para descobrir o total de pessoas que precisam estar contidas no raio.

```
target = get_covid_count(measure='deaths')
```

3. O arquivo *feather* que contém os setores censitários ao redor da localização do usuário é carregado na memória. Caso necessário, áreas adjacentes vão sendo adicionadas até que os setores censitários selecionados tenham uma população superior ao total de mortos por Covid-19 no Brasil.

```
gdf = find_user_area(point, target)
```

4. Alguns setores censitários são polígonos inválidos que se auto-intercepam. Para corrigir esse problema, um buffer com distância 0 é aplicado nas geometrias, [como especificado no manual do Shapely](https://shapely.readthedocs.io/en/latest/manual.html#object.buffer).

```
gdf["geometry"] = gdf.geometry.buffer(0)
```

5. Antes de passar para o cáculo do raio, o programa cria um [*spatial index*](https://automating-gis-processes.github.io/site/notebooks/L3/spatial_index.html) para otimizar as operações geoespaciais.

```
spatial_index = gdf.sindex
```

6. Aqui ocorre a parte mais densa do processamento, quando o programa computa o raio ao redor do usuário. 

```
radius_data = find_radius(point, gdf, spatial_index, target)
```

Essa função, por ser a mais complexa do programa, merece uma descrição mais detalhada.

a) De início, o ponto fornecido pelo usuário é colocado em cima do mapa.

b) Um buffer de 0.01 graus é aplicado no ponto, que assim se torna um polígono circular.

c) Verificamos então quais setores censitários fazem interseção com o círculo.

d) Calulamos o percentual de interseção de cada um desses setores e somamos a população de forma proporcional. Por exemplo, caso um setor censitário de 100 habitantes esteja completamente dentro do círculo, somamos as 100 pessoas que moram lá. Caso esse mesmo setor só esteja 30% dentro do círculo, somamos apenas 30 pessoas.

e) Caso a  população no raio seja inferior ao total de mortos por Covid-19 no Brasil, aumentamos o buffer em 50% e repetimos o processo a partir do passo C.

f) Definimos um intervalo de tolerância para a população que está dentro do círculo: entre 90% e 110% do total de mortos.

g) Definimos um degrau para alterar o tamanho do buffer a cada iteração subsequente: de início, 50%.

h) Caso o total de pessoas no círculo esteja dentro do intervalo de tolerância, a função se resolve e retorna as coordenadas do raio.

i) Caso o total de pessoas no círculo seja superior ao intervalo de tolerância, diminuímos o tamanho do raio pelo valor do degrau.

j) Caso o total de pessoas no círculo seja inferior ao intervalo de tolerância, aumentamos o tamanho do raio pelo valor do degrau.

k) Verificamos novamente quais setores censitários fazem interseção com o círculo.

l) Calulamos outra vez o percentual de interseção de cada um desses setores e somamos a população de forma proporcional.

m) Para as próximas iterações, o degrau é diminuído pela metade: em vez de 50%, a alteração de tamanho passa para 25%, 12.5%... e assim sucessivamente.

n) Se necessário, repetimos a operação a partir do item H.

7. O programa acessa a malha de municípios do Brasil para descobrir qual deles contém o ponto do usuário. Essas informações são salvas e retornadas ao fim da execução.

```
city_data = find_user_city(point, target)
```

8. É carregado o arquivo com os centróides dos municípios, que vai ser usado para calcular quais são as cidades mais próximas do usuário.

```
city_centroids = gpd.read_feather("../output/city_centroids.feather")
```

9. Usando a função `nearest_neighbor` do Shapely, o programa calcula qual é a cidade mais próxima do usuário que iria "desaparecer" - ou seja, que tem menos habitantes do que o total de mortes no Brasil

```
neighbor_data = find_neighboring_city(point, target, city_centroids)
```

10. Para destacar os efeitos da epidemia em centros urbanos grandes, o programa seleciona duas capitais: a primeira é a mais perto do usuário, escolhida usando o mesmo método do item 9. A segunda é escolhida de forma aleatória.

```
capitals_data = choose_capitals(point, city_data["code_muni"], city_centroids)
```

11. O programa devolve para o front-end um objeto JSON com todos os dados coletados.
