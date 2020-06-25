'''
This script will run through a cron job and 
will upadate the dynamic data od the application
daily
'''

import prepare_covid_count, prepare_capitals_radius

def main():

	prepare_covid_count.main()
	prepare_capitals_radius.main()

if __name__ == "__main__":
	main()