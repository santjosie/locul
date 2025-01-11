import requests
from requests.auth import HTTPBasicAuth
import json
import streamlit as st
import re
import time
from utils import session

def invoke(summary, description):
    path = "/3/issue"
    payload = json.dumps( {
      "fields": {
        "project": {
          "key": st.session_state['JIRA_PROJECT_KEY']
        },
        "issuetype": {
          "name": "Story"
        },
        "reporter": {
            "id": st.session_state['ATLASSIAN_USER_ID']
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
        url=st.session_state['JIRA_URL'] + path,
        data=payload,
        headers=st.session_state['ATLASSIAN_HEADERS'],
        auth=st.session_state['AUTH']
    )
    if response.status_code == 201:
        jira_key = json.loads(response.text)['key']
        jira_url = "https://" + st.session_state['ATLASSIAN_DOMAIN'] + ".atlassian.net/jira/software/c/projects/" + \
                   st.session_state['JIRA_PROJECT_KEY'] + "/issues/" + jira_key
     #   st.success("A new issue has been created in JIRA with key " + jira_key)
     #   st.markdown("[Click here top open JIRA](" + jira_url + ")")
        st.toast('User story created in JIRA with key '+ jira_key, icon='😍')
    else:
        st.error("Error while creating issue in JIRA")
        st.error(json.loads(response.text))

def push_to_jira(summary, description):
    if (st.session_state['ATLASSIAN_API_TOKEN']
            and st.session_state['ATLASSIAN_USER_NAME'] and st.session_state['ATLASSIAN_DOMAIN']
            and st.session_state['JIRA_PROJECT_KEY'] and st.session_state['ATLASSIAN_USER_ID']):
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
        url=st.session_state['JIRA_URL'] + path,
        headers=st.session_state['ATLASSIAN_HEADERS'],
        data=payload,
        auth=st.session_state['AUTH']
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
        if note['parentId'] is not None:
            notes.append({
                'title': note['title'],
                'body' : note['body']['storage']['value']
            })
    return notes

def get_release_notes():
    path = "/v2/spaces/" + st.session_state['CONFLUENCE_SPACE_ID'] +"/pages"
    response = requests.request(
        method="GET",
        url=st.session_state['CONFLUENCE_URL'] + path,
        headers=st.session_state['ATLASSIAN_HEADERS'],
        auth=st.session_state['AUTH'],
        params={
      "body-format": "storage",
      "limit": 5
    }
    )
    if response.status_code == 200:
        return parse_release_notes_response(json.loads(response.text))
    else:
        st.error("Error while pulling release notes from Confluence")
        st.error(response.text)

def write_to_confluence(title, body):
    path = "/v2/pages"
    payload = json.dumps({
        "spaceId": st.session_state['CONFLUENCE_SPACE_ID'],
        "status": "current",
        "title": title,
        "body": {
            "representation": "storage",
            "value": body
        }
    })

    response = requests.request(
        method="POST",
        url=st.session_state['CONFLUENCE_URL'] + path,
        headers=st.session_state['ATLASSIAN_HEADERS'],
        data=payload,
        auth=st.session_state['AUTH']
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