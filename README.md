# COVID-19-Dashboard
A personalised dashboard for displaying COVID-19 data and articles based on their local area.

---

**version 1.0.0**

Fetch and display relevent covid-19 data in a user friendly format.

A single place to filter information about the covid-19 pandemic.

---

**Updates**

No new updates

---

**Prerequisites**

The package heavily relies on the flask module to run properly in a user-friendly format.
Follow the instructions to install flask if it is not already installed.

To install any missing packages:
	-Open cmd
	-run the command: python3 -m pip install MODULE_NAME

	-Alternatly, running testing.py on its own (without pytest) will install any missing modules.
	-Open cmd
	-navigate to SERSION_1_0_0 directory
	-run the command: python3 testing.py

	-If pip requires updating:
	-run the command: python -m pip install --upgrade pip

---

**Usage**

Modules covid_data_handler and covid_news_handling are not directly part of the user interface and should not be edited by
any except those whom wish to build upon the framework provided by the package.

The module main.py will run the dashboard when executed in any python environment.

config.json is designed for user input. Any of the entries may be edited to customise the users experiance.

Testing.py can be run by anyone and will return tests on each of the functions in covid_data_handler.py and covid_news_handling.py
	-Install pytest:
	-open cmd
	-python3 -m pip install pytest

	-Run testing.py:
	-open cmd
	-navigate to the directory VERSION_1_0_0
	-run the command: python3 -m pytest testing.py
	-if any tests fail, run again when the issue has been resolved.

---

**Contributors**

Benjamin Finch

---

**Code Documentation - Developers Guide** 

	covid_api_request(location:str, location_type:str) -> dict
		-arguments: the identifiers of the data to be fetched

			-uses the imported Cov19API() function from the uk_covid_19 module
			-defines the data that is to be returned with the data list
			-establishes the format of the returned data with the data_structure dict

    		-output: the contents of the fetched json file

	parse_csv_data(csv_filename:dict) -> list
		-arguments: contents of a file fetched form the uk covid api
		-output: the list item from the input dictionary
	
	process_csv_data(covid_csv_data:list) -> tuple
		-arguments: a list of dictionaries from a json file

			-uses the get_latest_valid_entry function to get:
			-total number of deaths
			-current hospital cases
			-sum of the cases for 7 days
						
		-output: three data values extracted from the json data

	get_latest_valid_entry(name:str, input_dict:dict, values_to_skip = 0) -> int
		-argument: possition of each item in each line, list of items, values to skip

			-find the latest non-empty value in the specified position from all lines
			-ASSUMPTION: the file is sorted by date with the most recent date at the top
			-optionally ignore the first n non-empty value (default to not ignoring any)

		-output: the most up-to-date value in the possition

	schedule_covid_updates(update_interval:str) -> int
		-arguments: the time (24h clock) at which a function will run
			
			-use datetime to store the number of seconds in day up until now and the upadte point
			-calculate the number of seconds remaining until the specified time
			-adds 24 hours if the upadate is scheduled for tomorrow

    		-output: a time interval to delay data functions

covid_news_handling.py:
	External Modules:
		-json
		-requests
		-logging

	news_api_request(covid_terms:str) -> list
		-arguments: relevant search terms

    			-fetches the API data
    			-extracts the relevent entries
    			-uses try...except to deal with any incorrectly formatted dicts

    		-output: article data derived from the search terms

	update_news(list_of_articles:list, file_info:dict)
		-arguments: a list of diuctionarys describing a selection of news articles

			-adds a custom number of articles to the config, editable through the 'max_articles' variable
			-go though each item returned from the news api
			-uses try... except incase 'max_articles' has been changed to something other than an number
			
		-output: a limited selection of dictionaries sent to the config

main.py:
	External Modules:
		-json
		-sched
		-time
		-logging
		-flask -> (Flask, render_template, request)

	execute_updates(title: str, numbers:bool, new:bool, repeat:bool)
		-arguments: the description of a scheduled update
			
			-write the new info to a variable which is a replica of the config file
			-removes the update information from the config if it does not repeat

    		-output: the appropriate data updated in the config

	index() -> app
		-arguments: time, title, repeat?, update data?, update news?

			-schedules all the updates upon start or restart using schedule_covid_updates()
			-removes any updates if the user requests it
			-removes any articles if the users requests it
			-collect and submits any data on newly scheduled updates to the config copy
			-overwrites the config with all the new information using the file_contents copy
			
		-output: an entry for config.json with data about the shceduled update

---

**DEFAULT DATA**

max_articles = 5
covid_terms = Covid COVID-19 coronavirus
location = Exeter
location_type = ltla
nation_location = England
nation_type = nation
API_KEY = -

---
