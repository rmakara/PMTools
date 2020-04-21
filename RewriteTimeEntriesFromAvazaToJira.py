import datetime
import getpass
import json
from jira import JIRA
import requests

import iso8601

def get_timelogs_from_avaza(avaza_token, avaza_user_email, avaza_project_id, project_key, timelog_date_from, timelog_date_to):
    head = {'Authorization': 'Bearer ' + avaza_token}    

    if (timelog_date_to == '0'):
        timelog_date_to = datetime.today()

    # No need for pagitation. I assume single user will not have more than 1000 time entries in Avaza in a given period
    PAGE_SIZE = 1000
    page_number = 1
    result_avaza_timelogs = []
    
    i = 0   

    get_url = 'https://api.avaza.com/api/Timesheet?EntryDateFrom={0}&EntryDateTo={1}&pageSize={2}&pageNumber={3}&UserEmail={4}&ProjectID={5}'.format(timelog_date_from, timelog_date_to, PAGE_SIZE, page_number, avaza_user_email, avaza_project_id)    
    timesheets_json = requests.get(get_url, headers=head).json()

    for timesheet_entry in timesheets_json['Timesheets']:          
        if timesheet_entry['TaskTitle'].find(project_key) == 0: # is proper task assigned in Avaza? does it seem to be a Jira issue?                  
            project_key_last_index = timesheet_entry['TaskTitle'].find(" ") 

            issue_key = timesheet_entry['TaskTitle'][:project_key_last_index]
        
            result_avaza_timelogs.append(
                [
                    timesheet_entry['EntryDate'][:10],
                    timesheet_entry['TimesheetEntryID'],
                    issue_key,                    
                    round(timesheet_entry['Duration'], 2)
                ]
            )

    page_number = page_number + 1        
    
    return result_avaza_timelogs

def login_to_jira(jira_domain, jira_username):
    print('')
    print('Login to jira')
    
    print('What is your Jira token (https://confluence.atlassian.com/cloud/api-tokens-938839638.html)?')
    JIRA_TOKEN = getpass.getpass()  
    
    jira_client = JIRA(jira_domain, basic_auth=(jira_username, JIRA_TOKEN))

    return jira_client    

def add_time_entries_to_jira(jira_client, time_entries):
    print('Adding worklogs to Jira...')

    time_entries_count = len(time_entries)
    i = 0

    for time_entry in time_entries:
        i += 1
        if time_entry[3] > 0:
            print('Adding [' + str(i) + '/' + str(time_entries_count) + '] Date: ' + time_entry[0] + ', Timelog Avaza ID: ' + str(time_entry[1]) + ', Task: ' + time_entry[2] + ', Duration: ' + str(time_entry[3]))
            jira_client.add_worklog(issue = time_entry[2],
                                    started = iso8601.parse_date(time_entry[0]),
                                    timeSpent = str(time_entry[3]) + "h",
                                    comment = str(time_entry[1])
                                    )

### main :)

jira_domain = input("Jira Domain (e.g. https://your_company.atlassian.net): ")
jira_user_email = input("Your Jira email address (xxxxx@domain.pl): ")
print("What is your Avaza token?")
avaza_token = getpass.getpass()  
avaza_user_email = input("Your Avaza email address (xxxxx@domain.pl): ")
avaza_project_id = input("Avaza project ID (Avaza -> Projects -> Concrete project -> Rewrite it from URL): ")
project_key = input("Jira issue prefix: ")
timelog_date_from = input("Avaza timelogs, date from (format: yyyy-mm-dd): ")
timelog_date_to = input("Avaza timelogs, date to (format: yyyy-mm-dd): ")

jira_client = login_to_jira(jira_domain, jira_user_email)
avaza_time_entries = get_timelogs_from_avaza(avaza_token, avaza_user_email, avaza_project_id, project_key, timelog_date_from, timelog_date_to)

print('')
print('Please review the Avaza timelogs:')
print('')

print(avaza_time_entries)

if len(avaza_time_entries) > 0:
    print('')
    print('Are Avaza timelogs ok?')
    print('Are all the timelogs in Avaza associated with the tasks? If not, these entries will be skipped.')
    print('WARNING: This script does not look for duplicates. It may duplicate your worklogs in Jira.')
    print('If you want you can implement duplicate checks on your own. :p')
    print('')

    if "y" != input("Do you really want to migrate time entries to Jira? [y/n]: "):
        exit(0) 

    print('')

    add_time_entries_to_jira(jira_client, avaza_time_entries)

    print('')
    print('Done. Please verify migrated data in Jira. Bye.')

else:
    print('')
    print('Nothing to do. Bye.')
