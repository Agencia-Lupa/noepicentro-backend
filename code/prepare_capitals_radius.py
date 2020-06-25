'''
This script calculates the affected radius
for each capital in the country and saves it
to a JSON file
'''

from run_query import run_query
import json
from pprint import pprint

def compute(capitals_data):

	for index, capital in enumerate(capitals_data):

		output = run_query(capital["input_point"])

		capitals_data[index]["radius"] = output["radius"]

	return capitals_data

def save(data, fpath):
    
    fname = f"{fpath}capitals_radius.json"

    with open(fname, "w+") as file:

        json.dump(data, file)

def main():
	

	capitals_data = [ 

		{

			"code_muni": "431490", # First six IBGE digits

			"name_muni": "Porto Alegre",

			"name_state": "RS",

			"display_text": "da Usina do Gasômetro",

			"input_point": ["-30.0341319", "-51.2432707"]

		},

		{

			"code_muni": "355030",

			"name_muni": "São Paulo",

			"name_state": "SP",

			"display_text": "do MASP",

			"input_point": ["-23.5628876", "-46.6504141"]

		},

		{

			"code_muni": "330455",

			"name_muni": "Rio de Janeiro",

			"name_state": "RJ",

			"display_text": "do Maracanã",

			"input_point": ["-22.9120302", "-43.2319878"]

		},

	]


	compute(capitals_data)

	save(capitals_data, "../output/")

if __name__ == "__main__":
	main()