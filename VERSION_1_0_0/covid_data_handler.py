"""
Takes the input from the uk Cov19 API.
Extracs the requested statistics from a list of dicts.
returns the values requested by main.py
"""

import datetime as dt
import json
import logging
from uk_covid19 import Cov19API

#Thursday 12pm-3:30pm Inovation common room
#no lecture on thursday week 12

#Create and configure logger
#Structure log messages
log_format = '%(levelname)s %(asctime)s - %(message)s'
#open .log file
logging.basicConfig(filename = "main.log",
                    level = logging.INFO,
                    encoding = 'utf-8',
                    format = log_format,)
#creates object to log too

def parse_csv_data(csv_filename:dict) -> list:
    """
    arguments: contents of a file fetched form the api

    -If an empty item is passed to the funtion, it will return a valid dictionary with None values.
    output: the  item in the dict containing the relevent data, (an iterable list of dicts)
    """
    try:
        data = csv_filename['data']
    except IndexError:
        logging.error('covid_data_handler.pass_csv_data: No item (data) in csv_filename')
        data = [
            {'cumDailyNsoDeathsByDeathDate': None,
             'hospitalCases': None,
             'newCasesByPublishDate': None}
            ]
    return data

def get_latest_valid_entry(name:str, input_dict:dict, values_to_skip = 0) -> int:
    """
    argument: position of each item in each line, list of items,
    values to skip.

    -find the latest non-empty value in the specified position from
    all lines.
    -ASSUMPTION: the file is sorted by date with the most recent
    date at the top
    -optionally ignore the first n non-empty value (default
    to not ignoring any)

    output: the most up-to-date value in the position
    """
    #store the fetched value
    result = 0
    #note how many lines need to be ignored
    skipped_entries = 0

    #loop through every line in the file (to a point)
    try:
        for entry in input_dict:
            #skips all empty entries
            if entry[name] is not None:
                #skips any line swhich have already been counted
                if skipped_entries == values_to_skip:
                    result = entry[name]
                    break
                skipped_entries += 1
    except IndexError:
        logging.warning('covid_data_handler.get_latest_valid_entry: Too few entries')

    return result


def process_csv_data(covid_csv_data:list) -> tuple:
    """
    arguments: a list of dictionaries from a data file
    output: three data values for the sum of the cases in the last week, 
    the total cumulative deaths, and current hospital cases.
    """
    cases = 0

    logging.info('covid_data_handling.process_csv_data: Calculating statistics')

    #total number of deaths
    total_deaths = (get_latest_valid_entry('cumDailyNsoDeathsByDeathDate', covid_csv_data))

    #current hospital cases
    current_hospital_cases = (get_latest_valid_entry('hospitalCases', covid_csv_data))

    #sum of cases over 7 days
    for values in range(7):
        #The skipped value argument = values+1 becuase
        #the loop counts from 0 wheras we nned to start at 1
        cases += get_latest_valid_entry('newCasesByPublishDate', covid_csv_data, values+1)

    return cases, current_hospital_cases, total_deaths


def covid_api_request(location:str, location_type:str) -> dict:
    """
    arguments: the identifiers of the data to be fetched
    output: the raw contents of the fetched json file
    """

    logging.info('covid_data_handling.covid_api_request: Fetching Covid API')

    #defines the data that is to be returned
    data = ['areaType=' + location_type, 'areaName=' + location]

    #establishes the format of the returned data
    data_structure = {
        'date': 'date',
        'areaName': 'areaName',
        'areaCode': 'areaCode',
        'cumDailyNsoDeathsByDeathDate': 'cumDailyNsoDeathsByDeathDate',
        'hospitalCases': 'hospitalCases',
        'newCasesByPublishDate': 'newCasesByPublishDate' }

    #fetches the information
    api = Cov19API(filters = data, structure = data_structure)
    return api.get_json()


def schedule_covid_updates(update_interval:str) -> int:
    """
    arguments: the time (24h clock) at which a function will run
    output: a time interval to delay data functions
    """

    logging.info('covid_data_handling.schedule_covid_updates: Calculating seconds')

    #use datetime to store the number of seconds in day up until now and the update time
    now = dt.datetime.today()
    try:
        then = dt.datetime.strptime(update_interval, '%H:%M')

        #calculate the number of seconds remaining until the specified time
        seconds = 60*60*int(then.hour) + 60*int(then.minute) - 60*60*int(now.hour) - 60*int(now.minute)

    except ValueError:
        logging.warning('covid_data_handler.schedule_covid_updates: time not passed by dashboard.')
        seconds = 0

    #Will the update happen tomorrow?
    if seconds < 0:
        seconds += 24*60*60
    return seconds

#For testing purposes. DOES NOT CHANGE THE LIVE DATA!
if __name__ == '__main__':
    with open('config.json', 'r', encoding = 'ASCII') as read_config:
        file_contents = json.load(read_config)

    with open('test_dict.json', 'r', encoding = 'ASCII') as json_file:
        test_dict = json.load(json_file)

    local = covid_api_request(file_contents['location'], file_contents['location_type'])
    national = covid_api_request(file_contents['nation_location'], file_contents['nation_type'])

    #These lines are to compare with the data from config.json
    #If they are different something is wrong.
    print (process_csv_data(parse_csv_data(local)))
    print (process_csv_data(parse_csv_data(national)))

