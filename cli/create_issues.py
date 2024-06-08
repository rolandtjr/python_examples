from jira import JIRA
from jql_pygments import load_config

config = load_config()

jira_server = config["server"]
jira_username = config["username"]
jira_password = config["token"]

jira = JIRA(server=jira_server, basic_auth=(jira_username, jira_password))

projects = [
    'QUANTUM', 'NEBULA', 'GALACTIC', 'STELLAR', 'AETHER', 'NOVA', 'COSMIC', 'LUNAR', 'ASTRAL', 'PHOTON'
]

issue_type = 'Task'
summary_template = 'Issue {0} for project {1}'
description_template = 'Description for issue {0} in project {1}'

def create_issues(project_key, num_issues=20):
    for i in range(1, num_issues + 1):
        issue_dict = {
            'project': {'key': project_key},
            'summary': summary_template.format(i, project_key),
            'description': description_template.format(i, project_key),
            'issuetype': {'name': issue_type},
        }
        jira.create_issue(fields=issue_dict)
        print(f'Created issue {i} in project {project_key}')

for project in projects:
    create_issues(project)

print("Issue creation completed.")