#### Como usar?


1. Clone o repositório

2. Baixe [este arquivo](https://drive.google.com/file/d/1Qr4R7Cv5xl949IAjGA-78MjAgni9BNSa/view?usp=sharing) compactado e extraia no diretório `data`.

3. Instale os requerimentos em um ambiente virtual com o seguinte comando:

```
 pip install -r requirements.txt
```

_É muito provável que isso dê ruim, porque as dependencias do Geopandas são chatinhas de lidar e algumas não são distribuídas de forma zoada. Caso dê ruim, pode ser que seja necessário usar o Anaconda. Para isso, é importante ver a sessão [Installing from source](https://geopandas.org/install.html#installing-from-source) da documentação._

_Basicamente, precisamos dos seguintes pacotes: shapely, fiona, rtree, pygeos, geopandas, feather, geofeather. Destes, só o último não está disponível via conda install e precisa ser instalado via pip._  

5. Use ```python prepare.py``` para pré-processar diversos dados, o que vai otimizar o processo de cálculo 

6. Use ```python run_query.py lat lon``` para obter um objeto com as informações necessárias para personalizar a visualização de dados

7. O arquivo ```update.py``` deve ser executado repetidamente em um intervalo fixo de tempo via cron ou mecanismo semelhante. Ele é responsável pro atualizar a contagem de casos de covid-19 no país, além de já calcular previamente o raio nas principais cidades do país.

#### TO DO LIST:

[] Melhorar instruções de como instalar o GeoPandas/PyGEOS
[] Documentar a geração de pontos no README.
[] Colocar a geração de pontos no prepare.py (?)
