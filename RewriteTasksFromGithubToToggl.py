from github import Github
import TogglPy
import argparse
import getpass
import config

def get_issues_from_github():
    github_organization_name = raw_input('Github organization name: ')
    github_repository_name = raw_input('Github repository name: ')
    github_repository_fullname = github_organization_name + '/' + github_repository_name

    github_token = getpass.getpass()

    github_client = Github(github_token)
    github_repository = github_client.get_repo(github_repository_fullname)
    github_issue = github_repository.get_issues()

    github_issues = {}

    for issue in github_repository.get_issues():    
        github_issues[issue.number] = issue.title

    return github_issues

def add_issues_to_toggl(github_issues):
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
        issue_key = int(issue_key.replace('#', '', 1))
        issue_summary = issue['name'][key_last_idx+1:]
        toggl_issues[issue_key] = [issue['id'], issue_summary]

    github_issues_count = len(github_issues.items())

    for github_key, github_title in github_issues.items():
        i += 1
        data = {
            'task': {}
        }

        data['task']['name'] = "#" + str(github_key) + " " + github_title
        data['task']['pid'] = toggl_project_id
        data['task']['wid'] = config.toggl['workspace_id']

        if int(github_key) in toggl_issues:
            if "#" + str(github_key) + " " + github_title != toggl_issues[github_key]:        
                updated_count += 1
                print("Updating [{0}/{1}] {2} {3}.".decode('ascii', 'ignore').format(str(i), str(github_issues_count), github_key, github_title))
                toggl.putRequest('https://www.toggl.com/api/v8/tasks/{0}'.format(toggl_issues[github_key][0]), data)
        else:
            created_count += 1
            print("Creating [{0}/{1}] {2} {3}.".decode('ascii', 'ignore').format(str(i), str(github_issues_count), github_key, github_title))
            toggl.postRequest('https://www.toggl.com/api/v8/tasks', data)

    print('')
    print("Number of created Toggl tasks: " + str(created_count))
    print("Number of updated Toggl tasks: " + str(updated_count))

### main :)

github_issues = get_issues_from_github()
add_issues_to_toggl(github_issues)
