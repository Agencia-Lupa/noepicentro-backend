'''
This scripts saves the centroids of the
Brazilian cities in geofeather file, as well
as a bounding box for its polygons
'''

import geopandas as gpd
import pandas as pd
import warnings 

warnings.filterwarnings('ignore', message='.*initial implementation of Parquet.*')
warnings.filterwarnings('ignore', message='.*to re-project geometries to a projected CRS before this operation.')



def read_shapes(source):

	def standardize_columns(gdf):

		gdf = gdf.rename(columns={
				"CD_MUN":"code_muni",
				"NM_MUN": "name_muni",
				"SIGLA_UF": "name_state"

			})

		gdf.code_muni = gdf.code_muni.str.extract("(\d{6})")

		return gdf


	gdf = gpd.read_file(source)

	gdf = standardize_columns(gdf)

	def simplify(gdf):

		gdf.geometry = geometry.simplify(.1)

	return gdf

def read_population(source):

	df = pd.read_csv(source, dtype={"code_muni":str})

	return df

def add_state_data(df):

	corresp = {

		"11":"RO", 
		"12":"AC",
		"13":"AM",
		"14":"RR",
		"15":"PA",
		"16":"AP",
		"17":"TO",
		"22":"PI",
		"23":"CE",
		"24":"RN",
		"25":"PB",
		"26":"PE",
		"27":"AL",
		"28":"SE",
		"29":"BA",
		"31":"MG",
		"32":"ES",
		"33":"RJ",
		"35":"SP",
		"41":"PR",
		"42":"SC",
		"43":"RS",
		"50":"MS",
		"51":"MT",
		"52":"GO",
		"53":"DF"

	}


	df["code_state"] = df.code_muni.str.extract("(\d{2})")

	df["name_state"] = df["code_state"].map(corresp) # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.map.html 

	return df

def merge(gdf, df):
	
	gdf = gdf.merge(df)

	return gdf

def get_bbox(gdf):

	gdf[["minx", "miny", "maxx", "maxy"]] = gdf.geometry.bounds

	return gdf

def get_centroids(gdf):

	gdf.geometry = gdf.geometry.centroid

	return gdf


def save_file(gdf, fpath):

	gdf.to_feather(fpath)

def main():

	gdf = read_shapes("../data/geo_data/malha_brasil/br_municipios")

	df = read_population("../data/city_population.csv")

	# df = add_state_data(df)

	gdf = merge(gdf, df)

	save_file(gdf, "../output/city_outlines.feather")

	gdf = get_bbox(gdf)

	gdf = get_centroids(gdf)

	save_file(gdf, "../output/city_info.feather")

if __name__ == "__main__":
	
	main()
	

