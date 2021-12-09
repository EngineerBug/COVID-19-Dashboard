"""
test the functionality of the package
"""

import os
import json
import covid_news_handling as news
import covid_data_handler as data

with open('config.json', 'r', encoding = 'ASCII') as file:
    file_contents = json.load(file)

with open('test_dict.json', 'r', encoding = 'ASCII') as json_file:
    test_dict = json.load(json_file)

with open('test_dict.json', 'r', encoding = 'ASCII') as empty_file:
    empty_dict = json.load(empty_file)

#Test covid_data_handler
def test_covid_api_request():
    """
    makes sure the function fetches the correct data
    and that the data is formatted correctly
    """
    return_list = data.covid_api_request(file_contents['location'], file_contents['location_type'])
    assert isinstance(return_list, dict)
    assert len(return_list) == 4

def test_parse_csv_data():
    """
    tests if the function is returning the correct item from the input
    (a list of dictionarys)
    """
    info = data.parse_csv_data(test_dict)
    assert isinstance(info, list)
    assert len(info) == 14

def empty_test_parse_csv_data():
    """
    puts an empty file though parse_csv_data to test the try...except statement
    """
    null = data.parse_csv_data(empty_dict)
    assert isinstance(null, list)
    assert len(null) == 1

def test_process_csv_data():
    """
    gives the function a known input to test if the correct output is given
    (simultaniously tests get_latest_valid_entry() as it is inegral to
    process_csv_data working correctly.
    """
    cases, hospital_cases, deaths = data.process_csv_data(data.parse_csv_data(test_dict))
    assert cases == 240299
    assert hospital_cases == 7019
    assert deaths == 141544

def empty_test_process_csv_data():
    list_of_nothing = []
    cases, hospital_cases, deaths = data.process_csv_data(data.parse_csv_data(list_of_nothing))
    assert cases == 0
    assert hospital_cases == 0
    assert deaths == 0

def test_schedule_covid_updates():
    """
    because the time can be for the next day or later today,
    the time cannot be negative or above 24 hours.
    """
    time = "15:6"
    assert data.schedule_covid_updates(time) <= 24*60*60
    assert data.schedule_covid_updates(time) >= 0

#Test covid_news_handling
def test_news_api_request():
    """
    tests if the API request is only pulling on page at a time
    to conserve the 100 api requests. Also confirms if the
    APi reuqest is reuqesting anyhting at all.
    """
    articles = news.news_api_request(file_contents['covid_terms'])
    assert len(articles) == 20

def test_update_news():
    """
    makes sure that "max articles" is a valid charecter
    """
    assert file_contents['max_articles'] >= 0

def test_module_instilation():
    """
    tests if any third party modules are not installed.
    if not, they are automaticlly installed
    """
    #is requests installed?
    installed = 0
    try:
        import requests
        installed += 1
    except ImportError:
        os.system('cmd /k "python3 -m pip install requests"')

    #is uk_covid19 installed?
    try:
        from uk_covid19 import Cov19API
        installed += 1
    except ImportError:
        os.system('cmd /k "python3 -m pip install uk_covid19"')

    #is flask installed?
    try:
        from flask import Flask
        installed += 1
    except ImportError:
        os.system('cmd /k "python3 -m pip install flask"')

    #is datetime installed?
    try:
        import datetime
        installed += 1
    except ImportError:
        os.system('cmd /k "python3 -m pip install datetime"')

    assert installed == 4