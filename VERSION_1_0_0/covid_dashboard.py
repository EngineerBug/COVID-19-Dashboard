"""
arguments: the data stored in the config.json file
output: a rendered webpage using the index.html template
"""

import json
import sched
import time
import logging
from flask import Flask, render_template, request
import covid_data_handler as data
import covid_news_handling as news

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

app = Flask(__name__)

schedule = sched.scheduler(time.time, time.sleep)

with open('config.json', 'r', encoding = 'ASCII') as read_config:
    file_contents = json.load(read_config)

def execute_update(title: str, numbers:bool, new:bool, repeat:bool):
    """
    arguments: the description of a scheduled update
    output: the appropriate data updated in the config
    """

    logger.info('covid_dashboard.execute_update: Executing scheduled update')

    #Should the covid data be updated?
    if numbers:
        #fetches the new values
        local_data = data.parse_csv_data(data.covid_api_request(file_contents['location'], file_contents['location_type']))
        national_data = data.parse_csv_data(data.covid_api_request(file_contents['nation_location'], file_contents['nation_type']))

        #updates the config file
        file_contents['national_cases'], file_contents['hospital_cases'], file_contents['deaths'] = data.process_csv_data(national_data)
        file_contents['local_cases'], file_contents['local_hospital_cases'], file_contents['local_deaths'] = data.process_csv_data(local_data)

    #Should the news be updated?
    if new:
        news.update_news(news.news_api_request(file_contents['covid_terms']), file_contents)

    if repeat is not True:
        for item_no in range(len(file_contents['scheduled_updates'])):
            if file_contents['scheduled_updates'][item_no]['title'] == title:
                del (file_contents['scheduled_updates'][item_no])


@app.route('/index')
def index():
    """
    arguments: time, title, repeat?, update data?, update news?
    output: an entry for config.json with data about the scheduled update
    """

    logger.info('covid_dashboard.index: Rendering dashboard')

    #schedules all the updates upon start or restart
    for entry in file_contents['scheduled_updates']:
        schedule.enter(data.schedule_covid_updates(entry['time']), 1, execute_update,
                       (entry['title'], entry['data'], entry['news'], entry['repeat']),)

        schedule.run(blocking = False)

    #Does an update need to be removed?
    if request.args.get('update_item') is not None:
        update_list = file_contents['scheduled_updates']
        #Go through each listed update
        for entry_no, entry in enumerate(update_list):
            #Is the name the same as the request?
            if entry['title'] == request.args.get('update_item'):
                del update_list[entry_no]
                break

    #Does an article need to be removed?
    if request.args.get('notif') is not None:
        article_list = file_contents['current_articles']
        #Go through each listed article
        for item_no, item in enumerate(article_list):
            #Does the article match the deleted article?
            if item['title'] == request.args.get('notif'):
                file_contents['past_articles'].append(item['title'])
                del article_list[item_no]
                break

    #Has there been a new update submitted?
    if request.args.get('update') is not None:
        #detects the arguments returned by the html and updates config.json
        schedule_struct = {
            'time' : request.args.get('update'),
            'title' : request.args.get('two'),
            'content' : request.args.get('update'),
            'repeat' : False,
            'data' : False,
            'news' : False}

        #Should the update be repeated?
        if 'repeat' in request.args:
            schedule_struct['repeat'] = True
            schedule_struct['content'] += ', repeat'

        #Should the covid data be updated?
        if 'covid-data' in request.args:
            schedule_struct['data'] = True
            schedule_struct['content'] += ', covid data'

        #Should the news be updated?
        if 'news' in request.args:
            schedule_struct['news'] = True
            schedule_struct['content'] += ', news'

        file_contents['scheduled_updates'].append(schedule_struct)

    #adds dashboard info to config.json
    with open('config.json', 'w', encoding = 'ASCII') as write_file:
        json.dump(file_contents, write_file)

    return render_template('index.html',
                           title = 'Covid Updates',
                           image = 'Nurgle.png',
                           location = 'Exeter',
                           local_7day_infections = file_contents['local_cases'],
                           nation_location = 'England',
                           national_7day_infections = file_contents['national_cases'],
                           hospital_cases = 'Current hospital cases: '
                                            + str(file_contents['hospital_cases']),

                           deaths_total = 'Total deaths: ' + str(file_contents['deaths']),
                           news_articles = file_contents['current_articles'],
                           updates = file_contents['scheduled_updates']
                           )


if __name__ == "__main__":
    app.run(debug = True, port = 5000)
