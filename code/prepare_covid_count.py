'''
This script does the following dara processing tasks,
that are independent from user input:

- Find how many covid-19 deaths/cases we had in the country to this day and save the output as JSON
- Find how many covid-19 deaths/cases we had each city to this day and save the output as GeoJSON
'''

import gzip, json, requests
import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point
#from io import StringIO

def download():

    r = requests.get("https://data.brasil.io/dataset/covid19/caso.csv.gz")

    with open("../output/brasil-io-cases.csv.gz", 'wb') as f:

        for chunk in r.iter_content(chunk_size=1024):

            if chunk:

                f.write(chunk)

                f.flush()

def read_data():

    df = pd.read_csv("../output/brasil-io-cases.csv.gz", encoding="Latin5", dtype={"city_ibge_code":str})

    df = df [ df.is_last ]

    df = df [ df.place_type == "city" ]
    
    return df.reset_index(drop=True)

def get_covid_count(data, fpath):
    '''    
    Returns the current number of covid deaths
    and cases registered in the country and saves
    to a json file. The data source is Brasil.io's
    API
    '''

    def compute(data, measure):

        if measure == 'deaths':

            total = data.deaths.sum()

        elif measure == 'cases':

            total = data.confirmed.sum()

        return total

    def save(data, fpath):
        
        fname = f"{fpath}case_count.json"

        with open(fname, "w+") as file:

            json.dump(data, file)

    deaths = compute(data, measure='deaths')

    cases = compute(data, measure='cases')

    vanishing_cities = data [ data.estimated_population_2019 < deaths ].shape[0]

    data = {

      "time": str(data.date.max()),

      "deaths": int(deaths),

      "cases": int(cases),

      "vanishing_cities": int(vanishing_cities)

    }

    save(data, fpath)

def get_city_count(data, fpath):

    centroids = gpd.read_feather("../output/city_info.feather")

    centroids = centroids[["code_muni", "geometry"]]

    # We need 6 digits IBGE code
    data.city_ibge_code = data.city_ibge_code.str.extract("(\d{6})")

    # Fix for Vitória
    centroids.loc[centroids.code_muni == "320530", "geometry"] = Point([-40.297984, -20.277465])

    centroids = centroids.merge(data, left_on="code_muni", right_on="city_ibge_code")

    centroids = centroids[["geometry", "deaths"]]

    centroids = centroids[centroids.deaths > 0]

    # Round point size
    centroids.geometry = centroids.geometry.apply(lambda x: Point([round(coord, 2) for coord in x.coords[0]]))

    centroids.to_file(f"{fpath}/deaths.json", driver='GeoJSON')
    
def main():

    download()

    df = read_data()

    get_covid_count(
        data = df,
        fpath = "../output/"
    )

    get_city_count(
        data = df,
        fpath = "../output/"
    )

if __name__ == "__main__":
    main()