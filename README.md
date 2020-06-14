#### Como usar?


1. Clone o repositório

2. Baixe [este arquivo](https://drive.google.com/file/d/1OV8Vx78a362hBg5K2VDYsKhcZPYCVQwn/view?usp=sharing) compactado e extraia no diretório `data`.

3. Instale os requerimentos em um ambiente virtual com o seguintes comando:

```
 pip install -r requirements.txt
```

_É muito provável que isso dê ruim, porque as dependencias do Geopandas são chatinhas de lidar e algumas não são distribuídas de forma zoada. Caso dê ruim, pode ser que seja necessário usar o Anaconda. Para isso, é importante ver a sessão [Installing from source](https://geopandas.org/install.html#installing-from-source) da documentação._

_Basicamente, precisamos dos seguintes pacotes: shapely, fiona, rtree, pygeos, geopandas, feather, geofeather. Destes, só o último não está disponível via conda install e precisa ser instalado via pip._  

4. Extraia os componentes do arquivo `data/setores_censitarios_shp_reduzido.tar.xz` para um diretório com o mesmo nome.

5. Use ```python prepare_tracts.py``` para pré-processar os dados dos setores censitários. Isso pode demorar um bocado, mas vai gerar uma série de arquivos eficientes e otimizados, no novo diretório `setores_censitarios_divididos_feather`.

6. Use ```python find_radius.py lat lon``` para obter o raio ao redor de um par específico de coordenadas.

#### Jupyter Notebooks

Versões alternativas dos scrips estão disponíveis no formato `.ipynb`, caso seja necessário trabalhar em uma sessão interativa.