#!/usr/bin/env python
# coding: utf-8

'''
This script is similar to prepare_tracts.py, but slightly altered
to do the same for city outlines.
'''

#from geofeather import to_geofeather, from_geofeather
from shapely.geometry import Polygon, MultiPolygon, LineString
from shapely.ops import split
import geopandas as gpd
import pandas as pd
import glob, multiprocessing, os, re, shutil, sys

gpd.options.use_pygeos = True
pd.set_option('display.float_format', lambda x: '%.5f' % x)

def read_data(path_to_info, path_to_shp):
    
    '''
    Reads both the demographic information
    and the geographic outline of the city
    outline
    '''

    dtype = {

        "code_muni": str

    }

    info = pd.read_csv(path_to_info, dtype=dtype)

    
    dtype = { 
        
        "CD_MUN": str,

    }
    
    
    shp = gpd.read_file(path_to_shp, dtype=dtype)

    # Remove the columns that we don't need
    shp = shp.drop(["AREA_KM2", "NM_MUN", "SIGLA_UF"], axis=1)

    shp = shp.rename(columns={

        "CD_MUN": "code_muni",

    })

    shp.code_muni = shp.code_muni.str.extract("(\d{6})")


    return info, shp

def merge_info_and_shape(info, shp):
    
    '''
    Joins the demographic information
    with the correspoding geographic outline.
    Returns a geodataframe.
    '''
    
    shp = shp.merge(info, on="code_muni", suffixes=("","__y"))

    shp = shp.drop([column for column in shp.columns if "__y" in column], axis=1)

    return shp

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

    return [ split_rectangle for split_rectangle in rectangle.geoms ]

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

def compute_new_geometries(matches, area):
    '''
    Calculates how many people live in the intersecting polygons.
    Also returns an array with the intersecting shapes.
    '''

    def process_intersection(tract, polygon):

        intersection = tract.intersection(polygon)

        return intersection
    
    intersection = process_intersection(matches.geometry.values, area)

    matches['geometry'] = intersection

    matches = matches.reset_index(drop=True)

    return matches

def split_tracts(row, output_dir, sindex, tracts):
    '''
    Splits the census tracts in equally sized bounding boxes, 
    and saves each one to a .feather file to avoid a huge load time 
    when doing the proper data processing. Note that this function
    does alter the input geometries according to the interception with 
    the bounding box.
    '''

    def f(bbox, index, output_dir, sindex, tracts):
        '''
        The df.apply function above is simply a wrapper for this
        function, which does the work item by item
        '''

        # Finds the intersecting tracts and do the relevant computations
        matches = find_intersections(tracts, sindex, bbox)

        matches = compute_new_geometries(matches, bbox)

        # Adds relevant information to the bboxes dataframe

        fname =  f'bbox-{index}.feather'

        fpath = output_dir + fname
        
        # If relevant, saves
        if matches.shape[0] != 0:
            
            matches.to_feather(fpath)
            
        return pd.Series({
            "fpath": fpath,
        })
                
    #################
    ### EXECUTION ###
    #################
       
    bbox = row.geometry
    
    index = row.name
    
    return f(bbox, index, output_dir, sindex, tracts)



def main():    
        
    df, gdf = read_data("/app/data/city_population.csv", "/app/data/geo_data/malha_brasil/br_municipios/")

    gdf = merge_info_and_shape(df, gdf)

    gdf.geometry = gdf.geometry.buffer(0)
        
    sindex = gdf.sindex
        
    brazil_bbox = Polygon([
        [-74.3143068749,-34.2970741167],
        [-34.4119631249,-34.2970741167],
        [-34.4119631249,5.648611595],
        [-74.3143068749,5.648611595],
        [-74.3143068749,-34.2970741167]
    ])
    
    bboxes = divide_bbox(brazil_bbox, 20, 20)
    
    bboxes = gpd.GeoDataFrame(geometry=bboxes).reset_index().rename(columns={'index':'id_no'})
    
    bboxes.crs = gdf.crs
            
    # Make sure that the output directory is empty, avoiding overwrites

    directory =  "/app/output/municipios_divididos_feather/"

    if not os.path.exists(directory):
        
        os.makedirs(directory)
    
            
    for f in glob.glob(directory + "*"):
        
        os.remove(f)
    
    # Splits the tracts in bboxes, extracting the relevant information
    # Note that the function also saves files to the directory and
    # adjusting the geometries according to the intersections

    new_data = bboxes.apply(split_tracts, args=[directory, sindex, gdf], axis=1)
        
    bboxes['fpath'] = new_data["fpath"]
            
    # Remove from the df all the bounding boxes that contain no tracts - that is, that weren't saved
    saved_files = glob.glob(directory + "*.feather")
    meaningful_bboxes = [ int(re.search('bbox\-(\d+)\.feather', file).group(1)) for file in saved_files ]
    bboxes = bboxes.loc[meaningful_bboxes].reset_index(drop=True)

    # Finds the neighbors and counts them
    bboxes[['neighbors', 'neighbor_count']] = bboxes.apply(find_neighbors, args=[bboxes], axis=1)    

    # Saves an index
    bboxes.to_feather("/app/output/index_city_bboxes.feather")
    
    return bboxes


if __name__ == "__main__":
    main()

