'''
This script calculates the affected radius
for each capital in the country and saves it
to a JSON file
'''

from run_query import parse_input, get_covid_count, find_user_area, find_radius
import geopandas as gpd
import json

def compute(capitals_data):

    target = get_covid_count(measure='deaths')

    for index, capital in enumerate(capitals_data):

        point = capital["input_point"]

        point = parse_input(point)
 
        gdf = find_user_area(point, target)
            
        gdf["geometry"] = gdf.geometry.buffer(0)
            
        spatial_index = gdf.sindex
            
        radius_data = find_radius(point, gdf, spatial_index, target)

        output = {

            "radius": radius_data

        }

        capitals_data[index]["radius"] = output["radius"]

    return capitals_data

def save(data, fpath):
    
    fname = f"{fpath}capitals_radius.json"

    with open(fname, "w+") as file:

        json.dump(data, file)

def main():
    

    capitals_data = [

      {'bbox': [(-51.303245191, -30.269413694), (-51.011942199, -29.932302176)],
      'code_muni': '431490',
      'complement': 'ponto turístico da capital gaúcha',
      'display_text': {'place': 'Usina do Gasômetro', 'preffix': 'da'},
      'input_point': ['-30.0341319', '-51.2432707'],
      'name_muni': 'Porto Alegre',
      'name_state': 'RS'},

     {'bbox': [(-49.389338636, -25.645386219), (-49.185224862, -25.345066882)],
      'code_muni': '410690',
      'complement': 'parque no centro da cidade',
      'display_text': {'place': 'Passeio Público', 'preffix': 'do'},
      'input_point': ['-25.4251957', '-49.2675855'],
      'name_muni': 'Curitiba',
      'name_state': 'PR'},

     {'bbox': [(-48.613467449, -27.853768737), (-48.327875277, -27.267971679)],
      'code_muni': '420540',
      'complement': 'que liga a ilha ao continente',
      'display_text': {'place': 'Ponte Hercílio Luz', 'preffix': 'da'},
      'input_point': [' -27.593922', '-48.565862'],
      'name_muni': 'Florianópolis',
      'name_state': 'SC'},

     {'bbox': [(-46.826199, -24.008430999), (-46.365084, -23.356292999)],
      'code_muni': '355030',
      'complement': 'museu mais famoso da metrópole',
      'display_text': {'place': 'MASP', 'preffix': 'do'},
      'input_point': ['-23.561444', '-46.655910'],
      'name_muni': 'São Paulo',
      'name_state': 'SP'},

     {'bbox': [(-43.796101924, -23.082403038), (-43.0990394, -22.746054529)],
      'code_muni': '330455',
      'complement': 'maior estádio do país',
      'display_text': {'place': 'Maracanã', 'preffix': 'do'},
      'input_point': ['-22.9120302', '-43.2319878'],
      'name_muni': 'Rio de Janeiro',
      'name_state': 'RJ'},

     {'bbox': [(-44.063340601, -20.059699053), (-43.857223411, -19.776426423)],
      'code_muni': '310620',
      'complement': 'marco arquitetônico mineiro',
      'display_text': {'place': 'Praça da Liberdade', 'preffix': 'da'},
      'input_point': ['-19.932046', '-43.938043'],
      'name_muni': 'Belo Horizonte',
      'name_state': 'MG'},

     {'bbox': [(-54.924333854, -21.585103223), (-53.600442011, -20.165966339)],
      'code_muni': '500270',
      'complement': 'parque perto do centro da cidade',
      'display_text': {'place': 'Horto Florestal', 'preffix': 'do'},
      'input_point': ['-20.469733', '-54.623300'],
      'name_muni': 'Campo Grande',
      'name_state': 'MS'},

     {'bbox': [(-56.301892114, -15.750652547), (-55.480060956, -15.070064345)],
      'code_muni': '510340',
      'complement': 'no centro exato da América do Sul',
      'display_text': {'place': 'Obelisco do Centro Geodésico', 'preffix': 'do'},
      'input_point': ['-15.600615', '-56.100513'],
      'name_muni': 'Cuiabá',
      'name_state': 'MT'},

     {'bbox': [(-48.285828259, -16.049991675), (-47.308405545, -15.501819891)],
      'code_muni': '530010',
      'complement': 'projetada por Oscar Niemeyer',
      'display_text': {'place': 'Catedral Metropolitana', 'preffix': 'da'},
      'input_point': ['-15.7986852', '-47.8757942'],
      'name_muni': 'Brasília',
      'name_state': 'DF'},

     {'bbox': [(-49.446918957, -16.831813951), (-49.078018883, -16.453670227)],
      'code_muni': '520870',
      'complement': 'no setor central do município',
      'display_text': {'place': 'Monumento às Três Raças', 'preffix': 'do'},
      'input_point': ['-16.6798512', '-49.2558648'],
      'name_muni': 'Goiânia',
      'name_state': 'GO'},

     {'bbox': [(-37.17369134, -11.161602782), (-37.033470834, -10.862499166)],
      'code_muni': '280030',
      'complement': 'região turística da capital sergipana',
      'display_text': {'place': 'Passarela do Caranguejo', 'preffix': 'da'},
      'input_point': ['-10.992006', '-37.050950'],
      'name_muni': 'Aracaju',
      'name_state': 'SE'},

     {'bbox': [(-35.016695029, -8.155147785), (-34.859002808, -7.929199476)],
      'code_muni': '261160',
      'complement': 'perto do porto da cidade',
      'display_text': {'place': 'Marco Zero', 'preffix': 'do'},
      'input_point': ['-8.063183', '-34.871139'],
      'name_muni': 'Recife',
      'name_state': 'PE'},

     {'bbox': [(-44.413592618, -2.799234682), (-44.161684513, -2.473379042)],
      'code_muni': '211130',
      'complement': 'no centro histórico da capital maranhense',
      'display_text': {'place': 'Museu de Artes Visuais', 'preffix': 'do'},
      'input_point': ['-2.529128', ' -44.305966'],
      'name_muni': 'São Luís',
      'name_state': 'MA'},

     {'bbox': [(-38.699264042, -13.01732616), (-38.30433267, -12.73356241)],
      'code_muni': '292740',
      'complement': 'cartão postal da região',
      'display_text': {'place': 'Elevador Lacerda', 'preffix': 'do'},
      'input_point': ['-12.9744658', '-38.5131887'],
      'name_muni': 'Salvador',
      'name_state': 'BA'},

     {'bbox': [(-38.637902938, -3.894603063), (-38.401327688, -3.692025971)],
      'code_muni': '230440',
      'complement': 'conhecida como "coração da cidade"',
      'display_text': {'place': 'Praça do Ferreira', 'preffix': 'da'},
      'input_point': ['-3.7277894', '-38.5276207'],
      'name_muni': 'Fortaleza',
      'name_state': 'CE'},

     {'bbox': [(-60.802727218, -3.222208824), (-59.159948322, -1.924304438)],
      'code_muni': '130260',
      'complement': 'centro cultural de fama internacional',
      'display_text': {'place': 'Teatro Amazonas', 'preffix': 'do'},
      'input_point': ['-3.1301977', '-60.0232912'],
      'name_muni': 'Manaus',
      'name_state': 'AM'},

     {'bbox': [(-48.624408234, -1.526584746), (-48.296124213, -1.019426734)],
      'code_muni': '150140',
      'complement': 'na margem da Baía do Guajará',
      'display_text': {'place': 'Mercado Ver-o-Peso', 'preffix': 'do'},
      'input_point': ['-1.4525862', '-48.5038115'],
      'name_muni': 'Belém',
      'name_state': 'PA'}
    ]

    compute(capitals_data)

    save(capitals_data, "../output/")

if __name__ == "__main__":
    main()