##############################################################################
## Jira specifics

# Jira URL
JIRA_URL = 'https://yourdomain.atlassian.net/rest/api/3'
# Jira user credentials (incl. API token)
JIRA_ACCOUNT = ('email-from-JIRA-account', 'your-api-token')
# Jira project ID (short)
JIRA_PROJECT = 'KEY'
# Jira Query (JQL)
JQL = 'project=%s+AND+issueType=Epic+AND+resolution=Unresolved+ORDER+BY+createdDate+ASC&maxResults=100' % JIRA_PROJECT
# Jira Epic custom field
JIRA_EPIC_FIELD = 'customfield_10005'
# Jira Sprints custom field
JIRA_SPRINT_FIELD = 'customfield_10010'
# Jira story points custom field
JIRA_STORY_POINTS_FIELD = 'customfield_10014'

##############################################################################
## GitLab specifics

# GitLab URL
GITLAB_URL = 'https://lab.your-instance.com/api/v4'
# GitLab token will be used whenever the API is invoked
GITLAB_TOKEN = 'your-gitlab-token'
# GitLab group
GITLAB_GROUP = 'group-name'
# GitLab group id
GITLAB_GROUP_ID = 'group-id-number'
# Gitlab project with group/namespace
GITLAB_PROJECT = 'group-name/project-name'
# GitLab project id
GITLAB_PROJECT_ID = 'project-id-number'

# *False* if Jira / GitLab is using self-signed certificates, otherwise *True*
VERIFY_SSL_CERTIFICATE = True

# Jira username as key, GitLab as value
# Note: If you want dates and times to be correct, make sure every user is (temporarily) owner
USERNAMES_MAP = {
    # 'your-jira-user-1': 'your-gitlab-user1',
    # 'your-jira-user-2': 'your-gitlab-user2',
   
}

# Convert Jira issue types to Gitlab labels
# Note: If a Jira issue type isn't in the map, the issue will be skipped
# use whole list
ISSUE_TYPES_MAP = {
    'Bug': 'Bug',
    'Epic': 'Epic',
    'Improvement': 'Improvement',
    'New Feature': 'New Feature',
    'Spec approval': 'Spec approval',
    'Story': 'Story',
    'Task': 'Task',
    'Sub-Task': 'Sub-Task',
    'Technical task': 'Technical task'
}

# Convert Jira story points to Gitlab issue weight
STORY_POINTS_MAP = {
    1.0: 1,
    2.0: 2,
    3.0: 3,
    5.0: 5,
    8.0: 8,
    13.0: 13,
    21.0: 21,
}
