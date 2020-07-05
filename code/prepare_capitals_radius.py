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

        # SUL

        {

            "code_muni": "431490", # First six IBGE digits

            "name_muni": "Porto Alegre",

            "name_state": "RS",

            "display_text": "da Usina do Gasômetro",

            "complement": "ponto turístico da capital gaúcha",

            "input_point": ["-30.0341319", "-51.2432707"]

        },

        {

            "code_muni": "410690",

            "name_muni": "Curitiba",

            "name_state": "PR",

            "display_text": "do Passeio Público",

            "complement": "parque no centro da cidade",

            "input_point": ["-25.4251957", "-49.2675855"]

        },

        # SUDESTE


        {

            "code_muni": "355030",

            "name_muni": "São Paulo",

            "name_state": "SP",

            "display_text": "do MASP",

            "complement": "museu mais famoso da metrópole",

            "input_point": ["-23.5628876", "-46.6504141"]

        },

        {

            "code_muni": "330455",

            "name_muni": "Rio de Janeiro",

            "name_state": "RJ",

            "display_text": "do Maracanã",

            "complement": "maior estádio do país",

            "input_point": ["-22.9120302", "-43.2319878"]

        },


        # CENTRO-OESTE

        {

            "code_muni": "530010",

            "name_muni": "Brasília",

            "name_state": "DF",

            "display_text": "da Catedral Metropolitana",

            "complement": "projetada por Oscar Niemeyer",

            "input_point": ["-15.7986852", "-47.8757942"]

        },

        {

            "code_muni": "260620",

            "name_muni": "Goiânia",

            "name_state": "GO",

            "display_text": "do Monumento às Três Raças",

            "complement": "no setor central do município",

            "input_point": ["-16.6798512", "-49.2558648"]

        },

        # NORDESTE

        {

            "code_muni": "292740",

            "name_muni": "Salvador",

            "name_state": "BA",

            "display_text": "do Elevador Lacerda",

            "complement": "cartão postal da região",

            "input_point": ["-12.9744658", "-38.5131887"]

        },

        {

            "code_muni": "230440",

            "name_muni": "Fortaleza",

            "name_state": "CE",

            "display_text": "da Praça do Ferreira",

            "complement": "conhecida como \"coração da cidade\"",

            "input_point": ["-3.7277894", "-38.5276207"]

        },

        # NORTE

        {

            "code_muni": "130260",

            "name_muni": "Manaus",

            "name_state": "AM",

            "display_text": "do Teatro Amazonas",

            "complement": "centro cultural de fama internacional",

            "input_point": ["-3.1301977", "-60.0232912"]

        },

        {

            "code_muni": "150140",

            "name_muni": "Belém",

            "name_state": "PA",

            "display_text": "do Mercado Ver-o-Peso",

            "complement": "na margem da Baía do Guajará",

            "input_point": ["-1.4525862","-48.5038115"]

        },

    ]


    compute(capitals_data)

    save(capitals_data, "../output/")

if __name__ == "__main__":
    main()