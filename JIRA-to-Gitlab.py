import json

import requests
from requests.auth import HTTPBasicAuth
import re



##############################################################################
## General

# *False* if Jira / GitLab is using self-signed certificates, otherwise *True*
VERIFY_SSL_CERTIFICATE = True

##############################################################################
## Jira specifics

# Jira URL
JIRA_URL = 'https://jmaltd.atlassian.net/rest/api/3'
# Jira user credentials (incl. API token)
JIRA_ACCOUNT = ('calum.murray@jmaconsulting.biz', 'your-api-token')
# Jira project ID (short)
JIRA_PROJECT = 'ADMIN'
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
GITLAB_URL = 'https://lab.jmaconsulting.biz/api/v4'
# GitLab token will be used whenever the API is invoked
GITLAB_TOKEN = 'your-gitlab-token'
# GitLab group
GITLAB_GROUP = 'test-group'
# GitLab group id
GITLAB_GROUP_ID = '47'
# Gitlab project with group/namespace
GITLAB_PROJECT = 'test-group/test'
# GitLab project id
GITLAB_PROJECT_ID = '51'

##############################################################################
## Import configuration

# Add a comment with the link to the Jira issue
ADD_A_LINK = False
# Add an Epic to the GitLab issue
ADD_EPIC = False
# Add a milestone/sprint to the GitLab issue
ADD_SPRINT = False

# Jira username as key, GitLab as value
# Note: If you want dates and times to be correct, make sure every user is (temporarily) owner
USERNAMES_MAP = {
    # 'your-jira-user-1': 'your-gitlab-user1',
    # 'your-jira-user-2': 'your-gitlab-user2',
    'calum.murray@jmaconsulting.biz': 'calum',
    'joe.murray@jmaconsulting.biz': 'joe',
    'edsel.lopez@jmaconsulting.biz': 'edsel',
    'monish.deb@jmaconsulting.biz': 'monish',
    'seamus.lee@jmaconsulting.biz': 'seamus'
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


##############################################################################
# extract values from json
def json_extract(obj, key):
    """Recursively fetch values from nested JSON."""
    arr = []

    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v, in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif v == 'paragraph':
                    arr.append('<br/>')
                elif k == key:
                    if v is not None:
                        arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr
    separator = ' '
    values = separator.join(extract(obj, arr, key))
    return values


# GET request
def gl_get_request(endpoint):
    response = requests.get(
        GITLAB_URL + endpoint,
        headers={'PRIVATE-TOKEN': GITLAB_TOKEN},
        verify=VERIFY_SSL_CERTIFICATE
    )

    if response.status_code != 200:
        raise Exception("Unable to read data from %s!" % GITLAB_PROJECT_ID)

    return response.json()


# POST request
def gl_post_request(endpoint, data):
    response = requests.post(
        GITLAB_URL + endpoint,
        headers={'PRIVATE-TOKEN': GITLAB_TOKEN},
        verify=VERIFY_SSL_CERTIFICATE,
        data=data
    )

    print('response is =', response.status_code)
    if response.status_code != 201:
        raise Exception("Unable to write data from %s!" % GITLAB_PROJECT_ID)

    return response.json()


# POST request
def gl_put_request(endpoint, data):
    response = requests.put(
        GITLAB_URL + endpoint,
        headers={'PRIVATE-TOKEN': GITLAB_TOKEN},
        verify=VERIFY_SSL_CERTIFICATE,
        data=data
    )


    if response.status_code != 200:
        if response.status_code != 201:
            print(response.status_code)
            raise Exception("Unable to change data from %s!" % GITLAB_PROJECT_ID)

    return response.json()


# GET request
def jira_get_request(endpoint):
    response = requests.get(
        JIRA_URL + endpoint,
        auth=HTTPBasicAuth(*JIRA_ACCOUNT),
        verify=VERIFY_SSL_CERTIFICATE,
        headers={'Content-Type': 'application/json'}
    )

    if response.status_code != 200:
        raise Exception("Unable to read data from %s!" % JIRA_PROJECT)

    return response.json()


##############################################################################
## Early exit scenario

if not GITLAB_PROJECT_ID:
    # find out the ID of the project.
    for project in gl_get_request('/projects'):
        if project['path_with_namespace'] == GITLAB_PROJECT:
            GITLAB_PROJECT_ID = project['id']
            break

if not GITLAB_PROJECT_ID:
    raise Exception("Unable to find %s in GitLab!" % GITLAB_PROJECT)


##############################################################################

# Get milestone or create one
def get_milestone_id(title):
    for milestone in gl_milestones:
        if milestone['title'] == title:
            return milestone['id']

    # Milestone doesn't yet exist, so we create it
    # Note: Group Milestone MUST not exist
    milestone = gl_post_request('/projects/%s/milestones' % GITLAB_PROJECT_ID, {'title': title})
    gl_milestones.append(milestone)
    return milestone['id']


##############################################################################

# Get all milestones
gl_milestones = gl_get_request('/projects/%s/milestones' % GITLAB_PROJECT_ID)

# Get all GitLab members
gl_members = gl_get_request('/groups/%s/members' % GITLAB_GROUP_ID)

# Get Jira issues
jira_issues = jira_get_request('/search?jql=' + JQL)

for issue in jira_issues['issues']:
    with open('json_file.json', 'w') as json_file:
        json.dump(issue, json_file, indent=4, separators=(':', ','))
        print(json_file)

    jira_key = issue['key']
    jira_issue_type = issue['fields']['issuetype']['name']

    gl_issue_type = ''
    if jira_issue_type not in ISSUE_TYPES_MAP:
        print("Unknown issue type detected. Jira issue %s skipped" % jira_key)
        continue
    else:
        gl_issue_type = ISSUE_TYPES_MAP[jira_issue_type]

    ##################

    print("Start import of Jira issue %s" % jira_key)
    try:
        jira_title = issue['fields']['summary']
    except TypeError:
        jira_title = 'No title found on JIRA'
    try:
        jira_description = json_extract(issue['fields']['description']['content'], 'text')
    except TypeError:
        jira_description = 'No description found on JIRA'
    print("jira_description =", jira_description)
    try:
        jira_issue_status = issue['fields']['status']['statusCategory']['name']
    except TypeError:
        jira_issue_status = 'In Progress'
    jira_reporter = issue['fields']['reporter']['displayName']
    jira_date = issue['fields']['created']

    # Get Jira assignee
    jira_assignee = ''
    if issue['fields']['assignee'] is not None and issue['fields']['assignee']['displayName'] is not None:
        jira_assignee = issue['fields']['assignee']['displayName']

    # Get GitLab assignee
    gl_assignee_id = 0
    for member in gl_members:
        if member['name'] == jira_assignee:
            gl_assignee_id = member['id']
            break

    # Add GitLab issue type as label
    gl_labels = []
    gl_labels.append(gl_issue_type)

    # Add "In Progress" to labels
    if jira_issue_status == "In Progress":
        gl_labels.append(jira_issue_type)

    # Add Epic name to labels
    if ADD_EPIC and JIRA_EPIC_FIELD in issue['fields'] and issue['fields'][JIRA_EPIC_FIELD] is not None:
        epic_info = jira_get_request('/issue/%s/?fields=summary' % issue['fields'][JIRA_EPIC_FIELD])
        gl_labels.append(epic_info['fields']['summary'])

    # Add Jira ticket to labels
    gl_labels.append('jira-import::' + jira_key)

    # Use the name of the last Jira sprint as GitLab milestone
    gl_milestone = None
    if ADD_SPRINT and JIRA_SPRINT_FIELD in issue['fields'] and issue['fields'][JIRA_SPRINT_FIELD] is not None:
        for sprint in issue['fields'][JIRA_SPRINT_FIELD]:
            match = re.search(r'name=([^,]+),', sprint)
            if match:
                name = match.group(1)
        if name:
            gl_milestone = get_milestone_id(match.group(1))

    # Get Jira attachments and comments - might want to do separately
    jira_info = jira_get_request('/issue/%s/?fields=attachment,comment' % issue['id'])
    jira_info_formatted = json.dumps(jira_info, indent=3)
    print(jira_info_formatted)


    # Issue weight
    gl_weight = 0
    if JIRA_STORY_POINTS_FIELD in issue['fields'] and issue['fields'][JIRA_STORY_POINTS_FIELD]:
        gl_weight = STORY_POINTS_MAP[issue['fields'][JIRA_STORY_POINTS_FIELD]]

    # Create GitLab issue
    print("posting to gitlab")
    gl_issue = gl_post_request('/projects/%s/issues' % GITLAB_PROJECT_ID, {
        'assignee_ids': [gl_assignee_id],
        'title': jira_title,
        'description': jira_description,
        'milestone_id': gl_milestone,
        'labels': ", ".join(gl_labels),
        'weight': gl_weight,
        'created_at': jira_date
    })
    print("gl_issue =", gl_issue)

    gl_iid = gl_issue['iid']
    print(gl_iid)
    # post body using comment from jira_info, need to find a way to upload and use attachment
    # https://docs.gitlab.com/ce/api/projects.html#upload-a-file
    for comment in jira_info['fields']['comment']['comments']:
        author = comment['author']['displayName']
        print(author)
        content = json_extract(comment['body']['content'], 'text')
        print(content)
        comment_date = comment['created']
        gl_comment = gl_post_request('/projects/%s/issues/%s/notes' % (GITLAB_PROJECT_ID, gl_issue['iid']), {
            # trying to take the body from the comment - JIRA returns a lot of information
            # need to figure out how to have the author for the comment
            'body': "%(k)s: %(u)s" % {'k': author, 'u': content},
            'created_at': comment_date
        })

    # Add a comment with the link to the Jira issue
    if ADD_A_LINK:
        gl_post_request('/projects/%s/issues/%s/notes' % (GITLAB_PROJECT_ID, gl_issue['iid']), {
            'body': "Imported from Jira issue [%(k)s](%(u)sbrowse/%(k)s)" % {'k': jira_key, 'u': JIRA_URL}
        })

    # Change GitLab issue status
    if jira_issue_status == "Done":
        gl_put_request('api/v4/projects/%s/issues/%s' % (GITLAB_PROJECT_ID, gl_issue['iid']), {
            'state_event': 'close'
        })

