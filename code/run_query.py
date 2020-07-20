#!/usr/bin/env python
# coding: utf-8

from shapely.geometry import Point, Polygon
from shapely.ops import nearest_points
import pandas as pd
import geopandas as gpd
import glob, json, pygeos, random, sys, time, warnings

pd.options.mode.chained_assignment = None  # default='warn'
gpd.options.use_pygeos = True
warnings.filterwarnings(action = "ignore", 
                        category = UserWarning)

###############
### HELPERS ###
###############

def parse_input(argv):
    
    '''
    Parses the input that was passad 
    through the command line and returns
    a dictionary_object
    '''
                
    point = [float(coord.strip()) for coord in argv]
    
    point = Point(point[1], point[0]) # Shapely requires a lon, lat point

    return point

def get_covid_count(measure='deaths'):
    '''    
    Returns the current number of covid deaths
    or cases registered in the country according
    to that tha we have pre-processed
    '''
    
    with open("../output/case_count.json") as file:

        data = json.load(file)

    return data[measure]

def find_user_area(point, target):
    
    '''
    Finds the area that we will need to
    process according to the position of the point

    TO DO: use Pandas vectorization optimization instead of iterating through rows
    '''
    
    # A list with the quadrants whose population should be counted
    
    quadrants_to_count = [ ]
    
    # A list that will be filled with the ids of the quadrants that we need to load
    # That is, the quadrants to count plust its neighbors
    
    quadrants_to_load = [ ]
    
    # Loads the quadrant data
    
    reference_map = gpd.read_feather("../output/index_tracts_bboxes.feather")
       
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
        
        gdf = gpd.read_feather(fpath)
        
        gdfs.append(gdf)
        
    return pd.concat(gdfs)

def find_user_city(point, target, cities_info):
    '''
    Finds and loads the bounding box which contains
    the user city and retrieves its data
    '''

    # Loads the quadrant data
    
    reference_map = gpd.read_feather("../output/index_city_bboxes.feather")
       
    # Finds in which quadrant the point falls
    
    quadrant = reference_map[ reference_map.geometry.contains(point) ].reset_index(drop=True)

    assert quadrant.shape[0] == 1

    quadrant = gpd.read_feather(quadrant.loc[0, "fpath"])

    # Find in which city of the quadrant the point falls in

    # Weirdly, not all points within Brazil are contained in the shapefile
    # of its cities. Weird behavior happens in coastal cities such as Rio de Janeiro.
    # We will handle this issue now.

    user_city_code = quadrant[ quadrant.geometry.contains(point) ].reset_index(drop=True)

    if user_city_code.shape[0] < 1:

        # Find the closest city and assume we're there

        multipoint = cities_info.unary_union

        source, nearest = nearest_points(point, multipoint)

        nearest = cities_info [ cities_info.geometry == nearest ].reset_index(drop=True)

        assert nearest.shape[0] == 1

        # Fetches the data
        nearest = nearest.loc[0]

        code_muni = nearest['code_muni']

        user_city_code = code_muni #

    else:

        user_city_code = user_city_code.loc[0, 'code_muni']

    user_city = cities_info [ cities_info.code_muni == user_city_code].reset_index()

    assert user_city.shape[0] == 1

    # Takes the specific datapoint
    user_city = user_city.loc[0]

    # Extracts data
    code_muni = user_city["code_muni"]
    name_muni = user_city["name_muni"]
    name_state = user_city["name_state"]
    pop_2019 = int(user_city["pop_2019"])
    city_centroid = user_city["geometry"].centroid.coords[0]
    miny = user_city["miny"]
    maxy = user_city["maxy"]
    minx = user_city["minx"]
    maxx = user_city["maxx"]


    city_data = {

        "code_muni": code_muni,
        "name_muni": name_muni,
        "name_state": name_state,
        "pop_2019": pop_2019,
        "city_centroid": city_centroid,
        "bbox":[ (minx, miny), (maxx, maxy) ],
        "would_vanish": True if (pop_2019 <= target) else False

    }

    return city_data

def merge_tracts_and_shape(tracts, shp):
    
    return shp.merge(tracts, left_on='CD_GEOCODI', right_on='Cod_setor', how='left')

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
     
            
    # return matches, area

    #matches.to_feather(f"../output/radiuses/{point}.feather")
    
    radius_data = {

        "inner_point": point.coords[0],
        "outer_point": area.exterior.coords[0]

    }

    return radius_data

def find_neighboring_city(point, target, cities_info):

    '''
    Returns the city with less population than covid-cases
    that is nearest to the user input point
    '''

    cities_info = cities_info [ cities_info.pop_2019 <= target ]

    multipoint = cities_info.unary_union

    source, nearest = nearest_points(point, multipoint)

    nearest = cities_info [ cities_info.geometry == nearest ].reset_index(drop=True)

    assert nearest.shape[0] == 1

    # Fetches the data
    nearest = nearest.loc[0]

    code_muni = nearest['code_muni']
    name_muni = nearest['name_muni']
    name_state = nearest['name_state']
    pop_2019 = int(nearest['pop_2019'])
    city_centroid = nearest['geometry'].coords[0]

    # Gets bounding box data for this city
    miny = nearest["miny"]
    maxy = nearest["maxy"]
    minx = nearest["minx"]
    maxx = nearest["maxx"]

    neighbor_data = {

        "code_muni": code_muni,
        "name_muni": name_muni,
        "name_state": name_state,
        "pop_2019": pop_2019,
        "city_centroid": city_centroid,
        "bbox":[ (minx, miny), (maxx, maxy) ]

    }

    return neighbor_data

def choose_capitals(point, user_city_id, cities_info):
    '''
    Randomly selects two state capitals to highlight.
    Makes sure its not the user city.
    '''

    with open("../output/capitals_radius.json") as file:

        choices = json.load(file)

    # Don't select user city
    choices = [ item for item in choices if item["code_muni"] != user_city_id ]

    # First is the nearest capital
    capitals_info = cities_info [ cities_info.code_muni.isin([ item["code_muni"] for item in choices])]

    # Note that the geometry column is a Point item refering to the centroids
    multipoint = capitals_info.unary_union

    source, nearest = nearest_points(point, multipoint)

    nearest = capitals_info [ capitals_info.geometry == nearest ].reset_index(drop=True)

    assert nearest.shape[0] == 1

    nearest = nearest.loc[0, "code_muni"]

    first_capital = next(item for item in choices if item["code_muni"] == nearest)

    # Remove selection from choices
    choices = [ item for item in choices if item["code_muni"] != nearest ]

    # Second is randomly selected among the remaining options
    second_capital = random.sample(choices, 1)[0]
    
    # Returns selection as list
    return [ first_capital, second_capital ]

###############
### WRAPPER ###
###############

def run_query(point):

    
    # Gets information from the user input
    point = parse_input(point)

    # Opens the file with the current count of covid-19 deaths
    target = get_covid_count(measure='deaths')

    cities_info = gpd.read_feather("../output/city_info.feather")

    # Gets the parts of the census tracts with the user data that we need to load
    gdf = find_user_area(point, target)
        
    # Uses a buffer to avoid self-intercepting shapes
    gdf["geometry"] = gdf.geometry.buffer(0)
        
    # Creates a sindex to improve search
    spatial_index = gdf.sindex
        
    # Finds the area that we will need to highlight along with the respective population
    radius_data = find_radius(point, gdf, spatial_index, target)

    # Finds informations about the user city
    city_data = find_user_city(point, target, cities_info)

    # If the user city has less population than covid deaths,
    # the closest city that would vanish is itself
    if city_data["pop_2019"] <= target:
        neighbor_data = city_data.copy()

    # Else, finds the closest city with population smaller to the total deaths
    else:
        neighbor_data = find_neighboring_city(point, target, cities_info)

    # Selects two random capitals to highlight
    capitals_data = choose_capitals(point, city_data["code_muni"], cities_info)

    output = {

        "radius": radius_data,

        "user_city": city_data,

        "neighboring_city": neighbor_data,

        "capitals_to_highlight": capitals_data

    }

    from pprint import pprint

    pprint(output)

    return output


def main(argv):
        
    if len(argv) != 2:
        print("Usage: python find_radius.py lat lon")
        sys.exit(1)
    
    # Gets input from user and turns it into a shapely point
    return run_query(argv)
    
if __name__ == "__main__":

    main(sys.argv[1:])
