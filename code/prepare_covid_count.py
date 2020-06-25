'''
This script does the following dara processing tasks,
that are independent from user input:

- Find how many covid-19 deaths/cases we had in the country to this day
- Saves a JSON object with the radius data for each one of the 27 state capitals
'''

import json, requests
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

        return StringIO(r.text)

    def read_data(data):
        
        return pd.read_csv(data)

    def compute(data, measure):
        
        if measure == 'deaths':

            total = data.last_available_deaths.sum()

        elif measure == 'cases':

            total = data.last_available_confirmed.sum()


        else:
            raise(ValueError("Unknown measure"))

        return total

    def save(data, fpath):
        
        fname = f"{fpath}case_count.json"

        with open(fname, "w+") as file:

            json.dump(data, file)

    data = download(source)

    data = read_data(data)

    deaths = compute(data, measure='deaths')

    cases = compute(data, measure='cases')

    data = {

      "time": datetime.now().strftime("%d-%m-%Y-%H-%M-%S"),

      "deaths": int(deaths),

      "cases": int(cases)

    }

    save(data, fpath)
    
def main():

    get_covid_count(
        source = "https://brasil.io/dataset/covid19/caso_full/?place_type=state&is_last=True&format=csv", 
        fpath = "../output/"
    )

if __name__ == "__main__":
    main()