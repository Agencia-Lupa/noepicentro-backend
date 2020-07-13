'''
This scripts runs all the pre-processing routines
'''

import prepare_city_bboxes, prepare_tracts_bboxes, prepare_city_info, prepare_covid_count, prepare_capitals_radius, warnings

warnings.filterwarnings('ignore', message='.*initial implementation of Parquet.*')

def main():
	
	prepare_city_bboxes.main()
	prepare_tracts_bboxes.main()
	prepare_city_info.main()
	prepare_covid_count.main()
	prepare_capitals_radius.main()

if __name__ == "__main__":
	main()


