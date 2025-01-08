import requests
from requests.auth import HTTPBasicAuth
import json
import streamlit as st
import re
import time

ATLASSIAN_DOMAIN = st.secrets['ATLASSIAN_DOMAIN']
ATLASSIAN_PROJECT_KEY = st.secrets['ATLASSIAN_PROJECT_KEY']
ATLASSIAN_USER_NAME = st.secrets['ATLASSIAN_USER_NAME']
ATLASSIAN_USER_ID = st.secrets['ATLASSIAN_USER_ID']
ATLASSIAN_API_TOKEN = st.secrets['ATLASSIAN_API_TOKEN']

JIRA_URL = "https://" + ATLASSIAN_DOMAIN + ".atlassian.net/rest/api"
CONFLUENCE_URL = "https://" + ATLASSIAN_DOMAIN +".atlassian.net/wiki/api"
CONFLUENCE_SPACE_ID = "65978"
CONFLUENCE_PAGE_ID = "98309"
HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}
AUTH = HTTPBasicAuth(username=ATLASSIAN_USER_NAME, password=ATLASSIAN_API_TOKEN)

def configure_atlassian():
    if 'ATLASSIAN_API_TOKEN' in st.secrets and 'ATLASSIAN_USER_NAME' in st.secrets and 'ATLASSIAN_DOMAIN' in st.secrets and 'ATLASSIAN_PROJECT_KEY' in st.secrets and 'ATLASSIAN_USER_ID' in st.secrets:
      st.session_state['atlassian_api_token'] = st.secrets['ATLASSIAN_API_TOKEN']
      st.session_state['atlassian_user_name'] = st.secrets['ATLASSIAN_USER_NAME']
      st.session_state['atlassian_domain'] = st.secrets['ATLASSIAN_DOMAIN']
      st.session_state['atlassian_project_key'] = st.secrets['ATLASSIAN_PROJECT_KEY']
      st.session_state['atlassian_user_id']  = st.secrets['ATLASSIAN_USER_ID']
    else:
        with st.container():
            st.subheader("Atlassian JIRA configuration", help="For pushing user stories to JIRA, adding details of users for whom the requires Create Issue, Browse Projects and Modify Reporter permissions have been granted")
            st.session_state['atlassian_api_token'] = st.text_input(label="Enter your Atlassian API token")
            st.session_state['atlassian_user_name'] = st.text_input(label="Enter your Atlassian user name")
            st.session_state['atlassian_domain'] = st.text_input(label="Enter your Atlassian domain")
            st.session_state['atlassian_project_key'] = st.text_input(label="Enter your JIRA project key")
            st.session_state['atlassian_user_id'] = st.text_input(label="Enter the id of the user", help="Copy this from the URL when viewing the Atlassian profile page")

def invoke(summary, description):
    path = "/3/issue"
    payload = json.dumps( {
      "fields": {
        "project": {
          "key": st.secrets['ATLASSIAN_PROJECT_KEY']
        },
        "issuetype": {
          "name": "Story"
        },
        "reporter": {
            "id": st.secrets['ATLASSIAN_USER_ID']
        },
        "description": {
          "content": [
            {
              "content": [
                {
                  "text": description,
                  "type": "text"
                }
              ],
              "type": "paragraph"
            }
          ],
          "type": "doc",
          "version": 1
        },
        "summary": summary,
      },
      "update": {}
    })

    response = requests.request(
        method="POST",
        url=JIRA_URL + path,
        data=payload,
        headers=HEADERS,
        auth=AUTH
    )
    if response.status_code == 201:
        jira_key = json.loads(response.text)['key']
        jira_url = "https://" + st.secrets['ATLASSIAN_DOMAIN'] + ".atlassian.net/jira/software/c/projects/" + \
                   st.secrets['ATLASSIAN_PROJECT_KEY'] + "/issues/" + jira_key
     #   st.success("A new issue has been created in JIRA with key " + jira_key)
     #   st.markdown("[Click here top open JIRA](" + jira_url + ")")
        st.toast('User story created in JIRA with key '+ jira_key, icon='😍')
    else:
        st.error("Error while creating issue in JIRA")
        st.error(json.loads(response.text))

def push_to_jira(summary, description):
    if (st.secrets['ATLASSIAN_API_TOKEN']
            and st.secrets['ATLASSIAN_USER_NAME']and st.secrets['ATLASSIAN_DOMAIN']
            and st.secrets['ATLASSIAN_PROJECT_KEY'] and st.secrets['ATLASSIAN_USER_ID']):
        invoke(summary, description)
    else:
        st.error("Atlassian integration not configured. Enter details in the sidebar")

def get_unprocessed_issues():
    path = "/3/search/jql"
    payload = json.dumps({
      "expand": "renderedFields",
      "fields": ["issuekey","summary", "description"],
      "jql": "project=HUM AND cf[10072] is empty"
    })

    response = requests.request(
        method="POST",
        url=JIRA_URL + path,
        headers=HEADERS,
        data=payload,
        auth=HTTPBasicAuth(ATLASSIAN_USER_NAME, ATLASSIAN_API_TOKEN)
    )

    if response.status_code == 200:
        return parse_issues_response(json.loads(response.text))
    else:
        st.error("Error while pulling issues from JIRA")
        st.error(json.loads(response.text))

def process_issue_description(description):
    return description['content'][0]['content'][0]['text']

def parse_issues_response(response):
    issues = []
    for issue in response['issues']:
        issues.append({
            'key': issue['key'],
            'summary': issue['fields']['summary'],
            'description': re.sub(r'<.*?>', ' ', issue['renderedFields']['description']),
            'jira_url': issue['self']
        })
    return issues

def parse_release_notes_response(response):
    notes = []
    for note in response['results']:
        notes.append({
            'title': note['title']
        })
    return notes

def get_release_notes():
    path = "/v2/spaces/" + CONFLUENCE_SPACE_ID +"/pages"
    response = requests.request(
        method="GET",
        url=CONFLUENCE_URL + path,
        headers=HEADERS,
        auth=HTTPBasicAuth(ATLASSIAN_USER_NAME, ATLASSIAN_API_TOKEN)
    )
    if response.status_code == 200:
        return parse_release_notes_response(json.loads(response.text))
    else:
        st.error("Error while pulling release notes from Confluence")
        st.error(response.text)

def write_to_confluence(title, body):
    path = "/v2/pages"
    payload = json.dumps({
        "spaceId": CONFLUENCE_SPACE_ID,
        "status": "current",
        "title": title,
        "body": {
            "representation": "storage",
            "value": body
        }
    })

    response = requests.request(
        method="POST",
        url=CONFLUENCE_URL + path,
        headers=HEADERS,
        data=payload,
        auth=HTTPBasicAuth(ATLASSIAN_USER_NAME, ATLASSIAN_API_TOKEN)
    )

    if response.status_code == 200:
        return json.loads(response.text)
    elif response.status_code == 400:
        error = json.loads(response.text)
        if error['errors'][0]['title'] == "A page with this title already exists: A page already exists with the same TITLE in this space":
            title = title + " Copy " + str(int(time.time()))
            return write_to_confluence(title, body)
        else:
            st.error("Error while pushing release note to Confluence")
            st.error(response.text)
    else:
        st.error("Error while pushing release note to Confluence")
        st.error(response.text)