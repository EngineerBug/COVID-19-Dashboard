"""
arguments: news API, title and contents entries
output: structured data that can be processed by other modules
"""

import json
import requests
import logging

#Create and configure logger
#Structure log messages
log_format = '%(levelname)s %(asctime)s - %(message)s'
#open .log file
logging.basicConfig(filename = "main.log",
                    level = logging.INFO,
                    encoding = 'utf-8',
                    format = log_format,)
#creates object to log too
logger = logging.getLogger()

with open('config.json', 'r', encoding = 'ASCII') as read_config:
        file_contents = json.load(read_config)

def news_api_request(covid_terms:str) -> list:
    """
    arguments: relevant search terms

    -fetches the API data
    -extracts the relevent entries
    -uses try...except to deal with any incorrectly formatted dicts

    output: article data derived from the search terms
    """
    logger.info('covid_news_handling.news_api_request: Fetching news API')

    #assemble the link to the api
    api_key = file_contents["API_KEY"]
    url = ('https://newsapi.org/v2/everything?'
           'q=' + covid_terms + '&'
           'sortBy=popularity&'
           'apiKey=' + api_key)

    #get response object
    try:
        response = requests.get(url)
        articles = response.json()['articles']
    except ValueError:
        logger.warning('covid_news_handling.news_api_request: API failure')
        articles = [{'title':'Error', 'content':'News API failed'}]
    #process response object to eliminate needless data
    results = []

    #loops through the new list of articles
    for art in articles:
        #adds a dictionary of the data for each article to a list
        try:
            return_object = {'title': art['title'], 'content': art['content']}
        except IndexError:
            return_object = {'title': 'Error', 'content': 'return_object not structured how expected'}

        results.append(return_object)

    return results

def update_news(list_of_articles:list, file_info:dict):
    """
    arguments: a list of dictionaries describing a selection of news articles

    -has no return statement
    -updates the config as part of its function

    output: a limited selection of dictionaries sent to the config
    """
    file_info['current_articles'] = []

    logger.info('covid_dashboard.update_news: Writing news data to the config')

    #adds a custom number of articles to the config, editable through the 'max_articles' variable
    #go though each item returned from the news api
    for count, article in enumerate(list_of_articles):
        try:
            #Are there already the max number of articles selected?
            if len(file_info['current_articles']) < file_info['max_articles']:
                if article['title'] not in file_info['past_articles']:
                    #Add it to the list if there is space and the article has not been displayed yet.
                    file_info['current_articles'].append(article)
        except ValueError:
            logger.warning('covid_dashboard.update_news: max articles is invalid')
            file_info['max_articles'] = 5

#For testing purposes. DOES NOT CHANGE THE LIVE DATA!
if __name__ == '__main__':
    all_articles = news_api_request(file_contents['covid_terms'])
    for entry in all_articles:
        print (entry)