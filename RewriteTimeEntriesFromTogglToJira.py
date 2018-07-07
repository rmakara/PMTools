from __future__ import division
import datetime
import os, sys, inspect
import getpass
import json
from jira import JIRA
from math import ceil
import config

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

import TogglPy
import iso8601

def login_to_jira():
    print('What is your Jira password ({0})?'.format(config.jira['domain']))
    jira_password = getpass.getpass()
    jira_client = JIRA(config.jira['domain'], basic_auth=(config.jira['username'], jira_password))

    return jira_client

def get_toggl_client():
    toggl_client = TogglPy.Toggl()
    toggl_client.setAPIKey(config.toggl['token'])

    return toggl_client

def prepare_query_for_toggl():
    print('')
    print('Please specify the data in Toggl, that you need to rewrite.')
    date_from = raw_input("Date from (yyyy-mm-dd): ")
    date_to = raw_input("Date to (yyyy-mm-dd): ")
    project_id = raw_input("Toggl Project ID: ")
    user_id = raw_input("Toggl User ID (Use 0 for all users): ")

    query = {
        'workspace_id': config.toggl['workspace_id'],
        'since': date_from,
        'until': date_to,
        'billable': 'yes',
        'project_ids': project_id,
    }

    return query

def get_time_entries_from_toggl(query):
    toggl = get_toggl_client()
    response = toggl.getDetailedReport(query)
    num_pages = ceil(response['total_count'] / response['per_page'])

    print('')
    print('Collecting data from Toggl...')
    print('Number of time entries: ' + str(response['total_count']))
    print('Number of pages: ' + str(num_pages))
    print('Building Toggl time entries array...')
    print('')

    toggl_time_entries = []
    current_page = 0

    while num_pages > current_page:
        current_page += 1
        query['page'] = current_page
        print('Downloading page number: ' + str(current_page))
        if current_page > 1:
            response = toggl.getDetailedReport(query)

        for time_entry in response['data']:
            if time_entry['task'] is not None:
                key_last_idx = time_entry['task'].find(" ")
                issue_key = time_entry['task'][:key_last_idx]
                time_id = time_entry['id']
                time_user = time_entry['user']
                time_start = time_entry['start'][:19] + "+0100"
                time_end = time_entry['end'][:19] + "+0100"
                time_spent = time_entry['dur']
                time_desc = time_entry['description']
                toggl_time_entries.append([issue_key, time_id, time_user, time_start, time_end, time_spent, time_desc])

    return toggl_time_entries

def add_time_entries_to_jira(jira_client, time_entries):

    print('')
    print('Did you check if Toggl is ok?')
    print('Did everyone report the time?')
    print('Are all time entries associated with the tasks?')
    print('Is the billable property ok?')
    print('')

    if "y" != raw_input("Do you really want to save time entries in Jira? IMPORTANT: Script does not look for duplicates. It rewrites all the data in specified period of time. It may duplicate worklogs! [y/n]: "):
        exit(0) 

    print('')
    if "y" != raw_input("Really? It is very risky! You will not be able to rollback this operation! [y/n]: "):
        exit(0)     

    print('')
    print('Adding worklogs to Jira...')
    time_entries_count = len(time_entries)
    i = 0
    for time_entry in time_entries:
        i += 1
        if round(time_entry[5] / 60 / 1000, 0) > 0:
            print('Adding [' + str(i) + '/' + str(time_entries_count) + '] Toggl ID: ' + str(time_entry[1]) + ' by ' + time_entry[2])
            jira_client.add_worklog(issue = time_entry[0],
                                    started = iso8601.parse_date(time_entry[3]),
                                    timeSpent = str(round(time_entry[5] / 60 / 1000, 0)) + "m",
                                    comment = "Toggl ID: " + str(time_entry[1]) + "\nUser: " + time_entry[2]
                                    )

    print('')
    print('Done.')

### main :)

jira_client = login_to_jira()
toggl_time_entries = get_time_entries_from_toggl(prepare_query_for_toggl())
add_time_entries_to_jira(jira_client, toggl_time_entries)
