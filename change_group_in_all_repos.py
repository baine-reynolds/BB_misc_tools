import requests
import concurrent.futures

executor = concurrent.futures.ThreadPoolExecutor()
project_permissions = []
repo_permissions = []

from_group_name = ""    # Example: "old_group"
to_group_name = ""  # Example: "new_group"
bitbucket_url = ""  # Example: "https://bitbucket.example.com"
admin_username = "" # Example: "admin"
admin_password = "" # Example: "password"
session = requests.Session()
session.auth = (admin_username, admin_password)

def get_projects(project_endpoint, paged_start=None, paged_limit=None):
    while True:
        params = {'start': paged_start, 'limit': paged_limit}
        r = session.get(project_endpoint, params=params)
        r_data = r.json()
        for project_json in r_data['values']:
            yield project_json
        if r_data['isLastPage'] == True:
            return
        paged_start = r_data['nextPageStart']

def get_repos(repo_endpoint, paged_start=None, paged_limit=None):
    while True:
        params = {'start': paged_start, 'limit': paged_limit}
        r = session.get(repo_endpoint, params=params)
        r_data = r.json()
        for repo_json in r_data['values']:
            yield repo_json
        if r_data['isLastPage'] == True:
            return
        paged_start = r_data['nextPageStart']

def get_groups(group_endpoint, paged_start=None, paged_limit=None):
    while True:
        params = {'start': paged_start, 'limit': paged_limit}
        r = session.get(group_endpoint, params=params)
        r_data = r.json()
        for group_json in r_data['values']:
            yield group_json
        if r_data['isLastPage'] == True:
            return
        paged_start = r_data['nextPageStart']

def add_group(group_endpoint, permission_level):
    params = {'name': to_group_name, 'permission': permission_level}    
    session.put(group_endpoint, params=params)

def match_group(group_endpoint):
    for group_json in get_groups(group_endpoint):
        if from_group_name == group_json['group']['name']: # if "from" group exists...
            permission_level = group_json['permission'] # copies current permission level of "from" group
            print(f"Found {from_group_name} under {group_endpoint}.\n\tReplicating permisison level of {permission_level} to {to_group_name}.")
            add_group(group_endpoint, permission_level) # adds "to" group to the selected project/repo

def main():
    project_endpoint = (bitbucket_url + '/rest/api/1.0/projects')
    for project_json in get_projects(project_endpoint): # list all projects
        project_group_endpoint = (bitbucket_url + '/rest/api/1.0/projects/' + project_json['key'] + '/permissions/groups')
        future = executor.submit(match_group, project_group_endpoint)
        project_permissions.append(future)
        repo_endpoint = (bitbucket_url + '/rest/api/1.0/projects/' + project_json['key'] + '/repos')
        for repo_json in get_repos(repo_endpoint): # list all repos per project
            repo_group_endpoint = (bitbucket_url + '/rest/api/1.0/projects/' + project_json['key'] + '/repos/' + repo_json['slug'] + '/permissions/groups')
            future = executor.submit(match_group, repo_group_endpoint)
            repo_permissions.append(future)
    concurrent.futures.wait(project_permissions)
    concurrent.futures.wait(repo_permissions)

if __name__ == '__main__':
    main()