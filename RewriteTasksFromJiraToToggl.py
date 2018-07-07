from jira import JIRA
import TogglPy
import argparse
import getpass
import config

def login_to_jira():
    print('What is your Jira password ({0})?'.format(config.jira['domain']))
    jira_password = getpass.getpass()
    jira_client = JIRA(config.jira['domain'], basic_auth=(config.jira['username'], jira_password))

    return jira_client

def get_issues_from_jira():
    jira_client = login_to_jira()
    
    print('')
    jira_project_key = raw_input('Jira Project Key: ')
    jira_number_of_issues = raw_input('Number of issues to rewrite: ')

    jira_issues_json = jira_client.search_issues("project='{0}' ORDER BY created DESC".format(jira_project_key), maxResults=jira_number_of_issues)
    jira_issues = {}

    for issue in jira_issues_json:
        jira_issues[issue.key] = issue.fields.summary

    return jira_issues

def add_issues_to_toggl(jira_issues):
    toggl = TogglPy.Toggl()
    toggl.setAPIKey(config.toggl['token'])

    print('')
    toggl_project_id = raw_input('Toggl Project ID: ')
    print('')

    toggl_issues_json = toggl.request('https://www.toggl.com/api/v8/projects/{0}/tasks'.format(toggl_project_id))

    i = 0
    created_count = 0
    updated_count = 0
    toggl_issues = {}

    for issue in toggl_issues_json:
        key_last_idx = issue['name'].find(" ")
        issue_key = issue['name'][:key_last_idx]
        issue_summary = issue['name'][key_last_idx+1:]
        toggl_issues[issue_key] = [issue['id'], issue_summary]

    jira_issues_count = len(jira_issues.items())

    for jira_key, jira_summary in jira_issues.items():
        i += 1
        data = {
            'task': {}
        }

        data['task']['name'] = jira_key + " " + jira_summary
        data['task']['pid'] = toggl_project_id
        data['task']['wid'] = config.toggl['workspace_id']

        if jira_key in toggl_issues:
            if jira_summary != toggl_issues[jira_key]:        
                updated_count += 1
                print("Updating [{0}/{1}] {2} {3}.".decode('ascii', 'ignore').format(str(i), str(jira_issues_count), jira_key, jira_summary))
                toggl.putRequest('https://www.toggl.com/api/v8/tasks/{0}'.format(toggl_issues[jira_key][0]), data)
        else:
            created_count += 1
            print("Creating [{0}/{1}] {2} {3}.".decode('ascii', 'ignore').format(str(i), str(jira_issues_count), jira_key, jira_summary))
            toggl.postRequest('https://www.toggl.com/api/v8/tasks', data)

    print('')
    print("Number of created Toggl tasks: " + str(created_count))
    print("Number of updated Toggl tasks: " + str(updated_count))

### main :)

jira_issues = get_issues_from_jira()
add_issues_to_toggl(jira_issues)
