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
          'display_text': 'da Usina do Gasômetro',
          'input_point': ['-30.0341319', '-51.2432707'],
          'name_muni': 'Porto Alegre',
          'name_state': 'RS'},

         {'bbox': [(-49.389338636, -25.645386219), (-49.185224862, -25.345066882)],
          'code_muni': '410690',
          'complement': 'parque no centro da cidade',
          'display_text': 'do Passeio Público',
          'input_point': ['-25.4251957', '-49.2675855'],
          'name_muni': 'Curitiba',
          'name_state': 'PR'},

         {'bbox': [(-46.826199, -24.008430999), (-46.365084, -23.356292999)],
          'code_muni': '355030',
          'complement': 'museu mais famoso da metrópole',
          'display_text': 'do MASP',
          'input_point': ['-23.5628876', '-46.6504141'],
          'name_muni': 'São Paulo',
          'name_state': 'SP'},

         {'bbox': [(-43.796101924, -23.082403038), (-43.0990394, -22.746054529)],
          'code_muni': '330455',
          'complement': 'maior estádio do país',
          'display_text': 'do Maracanã',
          'input_point': ['-22.9120302', '-43.2319878'],
          'name_muni': 'Rio de Janeiro',
          'name_state': 'RJ'},

         {'bbox': [(-48.285828259, -16.049991675), (-47.308405545, -15.501819891)],
          'code_muni': '530010',
          'complement': 'projetada por Oscar Niemeyer',
          'display_text': 'da Catedral Metropolitana',
          'input_point': ['-15.7986852', '-47.8757942'],
          'name_muni': 'Brasília',
          'name_state': 'DF'},

         {'bbox': [(-49.446918957, -16.831813951), (-49.078018883, -16.453670227)],
          'code_muni': '520870',
          'complement': 'no setor central do município',
          'display_text': 'do Monumento às Três Raças',
          'input_point': ['-16.6798512', '-49.2558648'],
          'name_muni': 'Goiânia',
          'name_state': 'GO'},

         {'bbox': [(-38.699264042, -13.01732616), (-38.30433267, -12.73356241)],
          'code_muni': '292740',
          'complement': 'cartão postal da região',
          'display_text': 'do Elevador Lacerda',
          'input_point': ['-12.9744658', '-38.5131887'],
          'name_muni': 'Salvador',
          'name_state': 'BA'},

         {'bbox': [(-38.637902938, -3.894603063), (-38.401327688, -3.692025971)],
          'code_muni': '230440',
          'complement': 'conhecida como "coração da cidade"',
          'display_text': 'da Praça do Ferreira',
          'input_point': ['-3.7277894', '-38.5276207'],
          'name_muni': 'Fortaleza',
          'name_state': 'CE'},


         {'bbox': [(-60.802727218, -3.222208824), (-59.159948322, -1.924304438)],
          'code_muni': '130260',
          'complement': 'centro cultural de fama internacional',
          'display_text': 'do Teatro Amazonas',
          'input_point': ['-3.1301977', '-60.0232912'],
          'name_muni': 'Manaus',
          'name_state': 'AM'},

         {'bbox': [(-48.624408234, -1.526584746), (-48.296124213, -1.019426734)],
          'code_muni': '150140',
          'complement': 'na margem da Baía do Guajará',
          'display_text': 'do Mercado Ver-o-Peso',
          'input_point': ['-1.4525862', '-48.5038115'],
          'name_muni': 'Belém',
          'name_state': 'PA'}
        ]

    compute(capitals_data)

    save(capitals_data, "../output/")

if __name__ == "__main__":
    main()