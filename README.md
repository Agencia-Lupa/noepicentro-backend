#### Como usar?


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

Ou, caso prefira isntalar com outro método, veja a sessão[https://geopandas.org/install.html#using-the-optional-pygeos-dependency](https://geopandas.org/install.html#using-the-optional-pygeos-dependency) da documentação.

4. Caso queira gerar também os pontos que aparecem no mapa, execute ```python generate_points.py```. Isso deve demorar um bocado e é opcional.

5. Use ```python prepare.py``` para pré-processar diversos dados, o que vai otimizar o processo de cálculo 

6. Use ```python run_query.py lat lon``` para obter um objeto com as informações necessárias para personalizar a visualização de dados

7. O arquivo ```update.py``` deve ser executado repetidamente em um intervalo fixo de tempo via cron ou mecanismo semelhante. Ele é responsável pro atualizar a contagem de casos de covid-19 no país, além de já calcular previamente o raio nas principais cidades do país.