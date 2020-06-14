#!/usr/bin/env python
# coding: utf-8

# In[30]:


import multiprocessing
from geofeather import to_geofeather, from_geofeather
from shapely.geometry import Point, Polygon
import pandas as pd
import geopandas as gpd
import glob, random, sys, time

pd.options.mode.chained_assignment = None  # default='warn'
gpd.options.use_pygeos = True


# In[49]:


def read_data(path_to_tracts, path_to_shp):
    
    dtype = { 
        
        "CD_GEOCODI": str,
        "CD_GEOCODM": str,
        "CD_MUNICIP": str,
        "Cod_setor": str
        
    }
    
    tracts = pd.read_csv(path_to_tracts, dtype=dtype)
    
    shp = gpd.read_file(path_to_shp, dtype=dtype)
    
    return tracts, shp


# In[31]:


def random_points(n=1):
    
    '''
    Generates n random points in the country
    '''
    
    # Load the outline of Brazil
    polygon = gpd.read_file("https://servicodados.ibge.gov.br/api/v2/malhas?qualidade=1&formato=application/vnd.geo+json")
    
    polygon = polygon.loc[0, 'geometry']
        
    # Get's its bounding box
    minx, miny, maxx, maxy = polygon.bounds
    
    # Generates a random point within the bounding box
    # untill it falls within the country
    
    points = [ ]
    
    while len(points) < n:
        
        point = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
        
        if polygon.contains(point):
            
            points.append(point)
            
    return points


# In[46]:


def parse_input(argv):
    
    '''
    Parses the input that was passad 
    through the command line and returns
    a point
    '''
                
    point = [float(coord.strip()) for coord in argv]
    
    point = Point(point[1], point[0]) # Shapely requires a lon, lat point
        
    return point


# In[47]:


def covid_count(measure='deaths'):
    '''
    TO DO
    
    Returns the current number of covid deaths
    or cases registered in the Country
    '''
    
    return 100000


# In[48]:


def find_user_area(point, target):
    
    '''
    Finds the area that we will need to
    process according to the position of the point
    '''
    
    # A list with the quadrants whose population should be counted
    
    quadrants_to_count = [ ]
    
    # A list that will be filled with the ids of the quadrants that we need to load
    # That is, the quadrants to count plust its neighbors
    
    quadrants_to_load = [ ]
    
    # Loads the quadrant data
    
    reference_map = from_geofeather("../data/index_bboxes.feather")
       
    # Finds in which quadrant the point falls
    
    user_area = reference_map[ reference_map.geometry.contains(point) ].reset_index(drop=True)
        
    assert user_area.shape[0] == 1
        
    # At first, we will count the population in that particular quadrant
        
    quadrants_to_count.append(user_area.loc[0, 'id_no'])
    
    # And add itself and its neighbors to those we should load
    quadrants_to_load.append(user_area.loc[0, 'id_no'])
    
    quadrants_to_load.extend(user_area.loc[0, 'neighbors'].split("|"))

    # Checks if the population is enough. If not, add more quadrants
        
    population_in_area = reference_map[ reference_map.id_no.isin(quadrants_to_count)].total_population.sum()
    
    while population_in_area < target:
                                 
        # Adds the neighbors of all counted quadrants to those we should count
        
        for index, row in reference_map[ reference_map.id_no.isin(quadrants_to_count)].iterrows():
                
            quadrants_to_count.extend(row.neighbors.split("|"))
                                      
        quadrants_to_count = list(set(quadrants_to_count))
                                    
        
        # Adds the neighbors of the loaded neighbors to those we should load
        
        for index, row in reference_map[ reference_map.id_no.isin(quadrants_to_load)].iterrows():
                                     
            quadrants_to_load.extend(row.neighbors.split("|"))
                                    
        quadrants_to_load = list(set(quadrants_to_load))
        
        # Gets the new population
        
        population_in_area = reference_map[ reference_map.id_no.isin(quadrants_to_count)].total_population.sum()
    
    # Loads the data in
    
    gdfs = [ ]
    
    quadrants = reference_map [reference_map.id_no.astype(str).isin(quadrants_to_load) ]
    
    for index, row in quadrants.iterrows():
        
        fpath = row.fpath
        
        gdf = from_geofeather(fpath)
        
        gdfs.append(gdf)
        
    return pd.concat(gdfs)


# In[50]:


def merge_tracts_and_shape(tracts, shp):
    
    return shp.merge(tracts, left_on='CD_GEOCODI', right_on='Cod_setor', how='left')


# In[118]:


def find_radius(point, tracts, spatial_index, target):
    
    ########################
    ### HELPER FUNCTIONS ###
    ########################
    
    def find_intersections(tracts, spatial_index, area):
        '''
        Finds all the polygons that intersect a given radius
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

            return intersection, population_in_intersection

        intersection, population_in_intersection = process_intersection(matches.populacao_residente.values,
                                         matches.geometry.values,
                                         area)

        matches['geometry'] = intersection
        
        matches['population_in_intersection'] = population_in_intersection

        return matches
    
    #################
    ### EXECUTION ###
    #################
    
    checkpoint = time.time()
    
    total_people = 0
    
    radius = .01 # This unit is lat/lon degrees
    
    checkpoint_b = time.time()
    
    # While we don't meet the population target, we keep increasing the radius to grab more people
    while True:
                
        total_people = 0
        
        area = point.buffer(radius)
        
        matches = find_intersections(tracts, spatial_index, area)
        
        matches = compute_population_in_area(matches, area)
        
        total_people = round(matches.population_in_intersection.sum())
                        
        if total_people < target:
        
            radius = radius * 1.5
            
            continue
        
        # Else, finish the iteration
        else:
            
            break
            
            
    # Now we can move into the fine-tuning, removing excess population
    
    checkpoint_b = time.time()
    
    direction = 'shrink'
    
    fine_tune = .5
    
    max_tolerance = target * 1.1
    
    min_tolerance = target * 0.9
    
    while True:
                        
        if total_people > max_tolerance:
            
            new_direction = 'shrink'
    
            total_people = 0
            
            radius = radius * (1 - fine_tune)
            
            area = point.buffer(radius)
            
            matches = find_intersections(tracts, spatial_index, area)
        
            matches = compute_population_in_area(matches, area)

            total_people = round(matches.population_in_intersection.sum())
                        
            if total_people <= max_tolerance and total_people >= min_tolerance:
                
                break
                
        
        elif total_people < min_tolerance:
            
            new_direction = 'grow'
            
            total_people = 0
            
            radius = radius * (1 + fine_tune)
            
            area = point.buffer(radius)
            
            matches = find_intersections(tracts, spatial_index, area)
        
            matches = compute_population_in_area(matches, area)

            total_people = round(matches.population_in_intersection.sum())
            
            
            if total_people <= max_tolerance and total_people >= min_tolerance:
                
                break
                
        else: # It's equal
            
            break
                
        if new_direction != direction:
                        
            direction = new_direction
    
            fine_tune = fine_tune / 2
     
        
    matches = matches[["CD_GEOCODI", "geometry", "population_in_intersection"]]
    
    # to_geofeather(matches, f"../output/radiuses/{point}.feather")
    
    return matches, area


# In[140]:


def process_input(point):
    
    point = parse_input(point)
        
    # TO DO: discover how many covid-19 deaths we have at this point in time
    target = covid_count()
            
    # Gets the parts of the census tracts with the user data that we need to load
    gdf = find_user_area(point, target)
        
    # Uses a buffer to avoid self-intercepting shapes
    gdf["geometry"] = gdf.geometry.buffer(0)
        
    # Creates a sindex to improve search
    spatial_index = gdf.sindex
        
    # Finds the area that we will need to highlight along with the respective population
    matches, area = find_radius(point, gdf, spatial_index, target)

    # TO DO: save output as geofeather
    pass

    # Returns the point and it's respective radius as output
    # TO DO: for test purposes with Tiago only
    print(point.coords[0], area.exterior.coords[0])
    return point.coords[0], area.exterior.coords[0]


def main(argv):
        
    if len(argv) != 2:
        print("Usage: python lat lon")
        sys.exit(1)
    
    # Gets input from user and turns it into a shapely point
    return process_input(argv)
    
if __name__ == "__main__":

    main(sys.argv[1:])
