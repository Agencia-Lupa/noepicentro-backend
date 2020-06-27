'''
This script will pre-generate a collection of points
representing the population of each census tract in Brazil.
Note that the number is not 100% accurate. It relies on the
law of large numbers to achieve representative results.
'''

import geopandas as gpd
from multiprocessing import cpu_count, Pool
import numpy as np
import pandas as pd
from shapely.geometry import Point, Polygon, MultiPoint
from shapely.ops import unary_union
import glob, os, random, shutil

gpd.options.use_pygeos = True
pd.options.mode.chained_assignment = None  # default='warn'

def read_file(fpath):

	gdf = gpd.read_feather(fpath)

	#gdf = gdf[ [ "Cod_setor", "populacao_residente", "geometry"] ]

	return gdf

def handle_outpath(outpath):

	# Remove folder if it exists
	if os.path.exists(outpath):

		shutil.rmtree(outpath)

	# Create a new one
	os.makedirs(outpath)

def process_columns(gdf):

	gdf[["minx", "miny", "maxx", "maxy"]] = gdf.geometry.bounds

	gdf["bbox"] = gdf.geometry.envelope

	gdf["polygon_area"] = gdf.geometry.area

	gdf["bbox_area"] = gdf.bbox.area

	gdf["ratio"] = gdf.bbox_area / gdf.polygon_area

	gdf["points_to_add"] = gdf.populacao_residente * gdf.ratio # We have just estimated how many points do we need to generate in order to make the points who fall inside the polygon rerpresentative

	gdf = gdf [ [ "Cod_setor", "populacao_residente", "geometry", "minx", "miny", "maxx", "maxy", "points_to_add"] ]

	return gdf

def create_random_points(gdf):

	def create_random_points_(row):

		'''
		Generates n random points inside a polygon that envelopes
		each census tract. Note that some points may be generated
		outside the actual polygon and they will be clipped out.
		However, according to the LLN, a representative ammount
		of points will be generated within each tract. This is why
		we calculated the "points_to_add" column using a ration between
		the actual tract area and the polygon area.


		Source:
		https://stackoverflow.com/questions/19481514/how-to-get-a-random-point-on-the-interior-of-an-irregular-polygon

		'''

		# print(f"Looking at row {row.name}")

		n = row.points_to_add
		polygon = row.geometry
		cod_setor = str(row.Cod_setor)

		minx, miny, maxx, maxy = row.minx, row.miny, row.maxx, row.maxy

		if np.isnan(n):
		    n = 0
		else:
		    n = int(n)


		points = [ ]

		for i in range(n):

		    point = (random.uniform(minx, maxx), random.uniform(miny, maxy))
		             
		    point = ( round(point[0], 5), round(point[1], 5))
		    
		    point = Point(point)
		        
		    points.append(point)
		    
		points = [ point for point in points if polygon.contains(point)]

		# print(points)
		        
		points = gpd.GeoDataFrame(geometry=points)

		if points.shape[0] > 0:

			print(f"Saving tract {cod_setor}")

			outfile = f"../output/tract_points/{cod_setor}.json"

			points.to_file(outfile, driver="GeoJSON")


    #################
	### EXECUTION ###
    #################


    # Compute the points and save each tract to a file
	gdf.apply(create_random_points_, axis=1)


def parallelize(gdf, func):

	n_cores = 8#cpu_count()

	gdf = np.array_split(gdf, n_cores)

	pool = Pool(n_cores)

	pool.map(func, gdf)

	pool.close()

	pool.join()


def main():

	handle_outpath("../output/tract_points/")
	
	gdf = read_file("../output/setores_censitarios.feather")

	gdf = process_columns(gdf)

	parallelize(gdf, create_random_points)


if __name__ == "__main__":
	main()