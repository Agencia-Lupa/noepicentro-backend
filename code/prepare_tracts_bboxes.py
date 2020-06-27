#!/usr/bin/env python
# coding: utf-8

'''
In this script, we split the spaefiles in a 150 x 150 grid, allowing
for better performance when computing the affected area in the main
script
'''

#from geofeather import to_geofeather, from_geofeather
from shapely.geometry import Polygon, MultiPolygon, LineString
from shapely.ops import split
import geopandas as gpd
import pandas as pd
import glob, multiprocessing, os, re, shutil

gpd.options.use_pygeos = True
pd.set_option('display.float_format', lambda x: '%.5f' % x)

def read_data(path_to_tracts, path_to_shp):
    
    '''
    Reads both the demographic information
    and the geographic outline of the census
    tracts
    '''
    
    dtype = { 
        
        "CD_GEOCODI": str,
        "CD_GEOCODM": str,
        "CD_MUNICIP": str,
        "Cod_setor": str
        
    }
    
    tracts = pd.read_csv(path_to_tracts, dtype=dtype)
    
    shp = gpd.read_file(path_to_shp, dtype=dtype)
    
    return tracts, shp




def merge_tracts_and_shape(tracts, shp):
    
    '''
    Joins the demographic information
    with the correspoding geographic outline.
    Returns a geodataframe.
    '''
    
    return shp.merge(tracts, left_on='CD_GEOCODI', right_on='Cod_setor', how='left')




def divide_bbox(rectangle, nrows, ncols): 
    '''
    Divides a rectangular bounding box in
    rows and columns

    Reference: https://stackoverflow.com/questions/58283684/how-to-divide-a-rectangle-in-specific-number-of-rows-and-columns
    '''

    minx, miny, maxx, maxy = rectangle.bounds

    dx = (maxx - minx) / nrows  # width of a small part

    dy = (maxy - miny) / ncols  # height of a small part

    horizontal_splitters = [LineString([(minx, miny + i*dy), (maxx, miny + i*dy)]) for i in range(ncols)]

    vertical_splitters = [LineString([(minx + i*dx, miny), (minx + i*dx, maxy)]) for i in range(nrows)]

    splitters = horizontal_splitters + vertical_splitters

    for splitter in splitters:
        rectangle = MultiPolygon(split(rectangle, splitter))

    return [ split_rectangle for split_rectangle in rectangle ]




def find_neighbors(row, gdf):
    '''
    Finds all the polygons in the GeoDataFrame
    that are neighbors to the current row
    '''

    neighbors = gdf [ ~gdf.geometry.disjoint(row.geometry)].id_no.astype(str).tolist() 
    
    neighbor_count = len(neighbors)
    
    neighbors = "|".join(neighbors)

    return pd.Series({
        "neighbors": neighbors,
        "neighbor_count": neighbor_count
    })




def find_intersections(tracts, spatial_index, area):
    '''
    Finds all the polygons that intersect a given area
    '''
    
    # Uses Geopandas/PyGeos rtree to pre-filter the tracts
    nearby_index = list(spatial_index.intersection(area.bounds))
    
    nearby_tracts = tracts.iloc[nearby_index]

    # Selects the tracts that do intersect with the area
    matches = nearby_tracts [ nearby_tracts.geometry.intersects(area)]

    return matches


def compute_population_in_area(matches, area):
    '''
    Calculates how many people live in the intersecting polygons.
    Also returns an array with the intersecting shapes.
    '''

    def process_intersection(population, tract, polygon):

        intersection = tract.intersection(polygon)

        intersection_percentage = intersection.area / tract.area 

        population_in_intersection = population * intersection_percentage

        return intersection, intersection_percentage, population_in_intersection
    
    

    intersection, intersection_percentage, population_in_intersection = process_intersection(matches.populacao_residente.values,
                                     matches.geometry.values,
                                     area)

    matches['geometry'] = intersection
    
    matches['INTERSECT'] = intersection_percentage.round(2)

    matches['POP_INTER'] = population_in_intersection.round()

    return matches.reset_index(drop=True)




def split_tracts(row, output_dir, sindex, tracts):
    '''
    Splits the census tracts in equally sized bounding boxes, 
    and saves each one to a .feather file to avoid a huge load time 
    when doing the proper data processing. Note that this function
    does alter the input geometries and their populations according
    to the interception with the bounding box.
    '''

    def f(bbox, index, output_dir, sindex, tracts):
        '''
        The df.apply function above is simply a wrapper for this
        function, which does the work item by item
        '''

        # Finds the intersecting tracts and do the relevant computations

        matches = find_intersections(tracts, sindex, bbox)

        matches = compute_population_in_area(matches, bbox)

        # Adds relevant information to the bboxes dataframe

        total_population = matches.POP_INTER.sum()     

        fname =  f'bbox-{index}.feather'

        fpath = output_dir + fname
        
        # If relevant, saves
        if matches.shape[0] != 0:
            
            matches.to_feather(fpath)
            
        return pd.Series({
            "fpath": fpath,
            "total_population": total_population
        })
                
    #################
    ### EXECUTION ###
    #################
       
    bbox = row.geometry
    
    index = row.name
    
    return f(bbox, index, output_dir, sindex, tracts)




def main():    
        
    df, gdf = read_data("../data/tracts_basic_data.csv","../data/geo_data/setores_censitarios_shp_reduzido/")
    
    gdf = merge_tracts_and_shape(df, gdf)

    gdf.to_feather("../output/setores_censitarios.feather")    
    
    gdf.geometry = gdf.geometry.buffer(0)
        
    sindex = gdf.sindex
        
    brazil_bbox = Polygon([
        [-74.3143068749,-34.2970741167],
        [-34.4119631249,-34.2970741167],
        [-34.4119631249,5.648611595],
        [-74.3143068749,5.648611595],
        [-74.3143068749,-34.2970741167]
    ])
    
    
    bboxes = divide_bbox(brazil_bbox, 150, 150)
    
    bboxes = gpd.GeoDataFrame(geometry=bboxes).reset_index().rename(columns={'index':'id_no'})
    
    bboxes.crs = gdf.crs
            
    # Make sure that the output directory is empty, avoiding overwrites

    directory =  "../output/setores_censitarios_divididos_feather/"

    if not os.path.exists(directory):
        
        os.makedirs(directory)
    
            
    for f in glob.glob(directory + "*"):
        
        os.remove(f)
    
    # Splits the tracts in bboxes, extracting the relevant information
    # Note that the function also saves files to the directory and
    # adjusts the population according to the intersections

    new_data = bboxes.apply(split_tracts, args=[directory, sindex, gdf], axis=1)
        
    bboxes['fpath'] = new_data["fpath"]
    
    bboxes['total_population'] = new_data["total_population"]
        
    # Remove from the data table all the bounding boxes that contain no tracts
    
    saved_files = glob.glob(directory + "*.feather")
        
    meaningful_bboxes = [ int(re.search('bbox\-(\d+)\.feather', file).group(1)) for file in saved_files ]
    
    bboxes = bboxes.loc[meaningful_bboxes].reset_index(drop=True)

    # Finds the neighbors and counts
    
    bboxes[['neighbors', 'neighbor_count']] = bboxes.apply(find_neighbors, args=[bboxes], axis=1)    

    bboxes.to_feather("../output/index_tracts_bboxes.feather")
    
    return bboxes


if __name__ == "__main__":
    main()

