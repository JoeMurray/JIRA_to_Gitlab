# JIRA_to_Gitlab
A script to migrate issues from JIRA to Gitlab

## Features
Migrates issues
Migrates comments on issues
Migrates files embedded in issue descriptions or comments
Migrates JIRA issue types to gitlab labels, eg TASK
Migrates JIRA issue code to gitlab label, eg ADMIN-1
Migrates @mentions as text.


## Limitations
Issues and comments are not created in gitlab by the user running the script
- workaround: comments are prefaced by text name of JIRA user that created comment in JIRA


## TODO
- fix up names
- fix closed/open
