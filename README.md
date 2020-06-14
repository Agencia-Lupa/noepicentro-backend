#### Como usar?

1. Instale os requerimentos em um ambiente virtual com o seguintes comando:

```
 pip install -r /path/to/requirements.txt
```

_É muito provável que isso dê ruim, porque as dependencias do Geopandas são chatinhas de lidar e algumas não são distribuídas de forma zoada. Caso dê ruim, pode ser que seja necessário usar o Anaconda. Para isso, é importante ver a sessão [Installing from source](https://geopandas.org/install.html#installing-from-source) da documentação._

_Basicamente, precisamos dos seguintes pacotes: shapely, fiona, rtree, pygeos, geopandas, feather, geofeather. Destes, só o último não está disponível via conda install e precisa ser instalado via pip._  

2. Extraia os componentes do arquivo `data/setores_censitarios_shp_reduzido.tar.xz` para um diretório com o mesmo nome.

3. Use ```python preare_tracts.py``` para pré-processar os dados dos setores censitários. Isso pode demorar um bocado, mas vai gerar uma série de arquivos .feather, que são eficientes e otimizados, no novo diretório `setores_censitarios_divididos_feather`.

4. Use ```python find_radius.py lat lon``` para obter o raio ao redor de um par específico de coordenadas.

#### Jupyter Notebooks

Versões alternativas dos scrips estão disponíveis no formato `.ipynb`, caso seja necessário trabalhar em uma sessão interativa.