'''
This script does the following dara processing tasks,
that are independent from user input:

- Find how many covid-19 deaths/cases we had in the country to this day
- Saves a JSON object with the radius data for each one of the 27 state capitals
'''

import gzip, json, requests
import pandas as pd
from datetime import datetime
from io import StringIO

def get_covid_count(source, fpath):
    '''    
    Returns the current number of covid deaths
    and cases registered in the country and saves
    to a json file. The data source is Brasil.io's
    API
    '''

    def download(source):

        r = requests.get(source)

        with open("../output/brasil-io-cases.csv.gz", 'wb') as f:

            for chunk in r.iter_content(chunk_size=1024):

                if chunk:

                    f.write(chunk)

                    f.flush()

    def read_data():

        df = pd.read_csv("../output/brasil-io-cases.csv.gz", encoding="Latin5")

        df = df [ df.is_last ]

        df = df [ df.place_type == "city" ]
        
        return df

    def compute(data, measure):

        if measure == 'deaths':

            total = data.deaths.sum()

        elif measure == 'cases':

            total = data.confirmed.sum()


        else:
            raise(ValueError("Unknown measure"))

        return total

    def save(data, fpath):
        
        fname = f"{fpath}case_count.json"

        with open(fname, "w+") as file:

            json.dump(data, file)

    download(source)

    data = read_data()

    deaths = compute(data, measure='deaths')

    cases = compute(data, measure='cases')

    vanishing_cities = data [ data.estimated_population_2019 < cases ].shape[0]

    data = {

      "time": str(data.date.max()),

      "deaths": int(deaths),

      "cases": int(cases),

      "vanishing_cities": int(vanishing_cities)

    }

    save(data, fpath)
    
def main():

    get_covid_count(
        source = "https://data.brasil.io/dataset/covid19/caso.csv.gz",
        fpath = "../output/"
    )

if __name__ == "__main__":
    main()