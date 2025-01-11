import streamlit as st
from requests.auth import HTTPBasicAuth

def atlas_session():
    st.session_state["ATLASSIAN_STATUS"] = True
    st.session_state['MODEL'] = 'mistral-large'
    st.session_state['TOP_P'] = 0.4
    st.session_state['TEMPERATURE'] = 0.7
    st.session_state['MAX_TOKENS'] = 4096
    st.session_state['NUM_CHUNKS'] = 3

    if 'ATLASSIAN_API_TOKEN' in st.secrets:
        st.session_state["ATLASSIAN_API_TOKEN"] = st.secrets['ATLASSIAN_API_TOKEN']
    elif 'ATLASSIAN_API_TOKEN' not in st.session_state:
        st.session_state["ATLASSIAN_STATUS"] = False

    if 'ATLASSIAN_USER_NAME' in st.secrets:
        st.session_state["ATLASSIAN_USER_NAME"] = st.secrets['ATLASSIAN_USER_NAME']
    elif 'ATLASSIAN_USER_NAME' not in st.session_state:
        st.session_state["ATLASSIAN_STATUS"] = False

    if 'ATLASSIAN_DOMAIN' in st.secrets:
        st.session_state["ATLASSIAN_DOMAIN"] = st.secrets['ATLASSIAN_DOMAIN']
    elif 'ATLASSIAN_DOMAIN' not in st.session_state:
        st.session_state["ATLASSIAN_STATUS"] = False

    if 'JIRA_PROJECT_KEY' in st.secrets:
        st.session_state["JIRA_PROJECT_KEY"] = st.secrets['JIRA_PROJECT_KEY']
    elif 'JIRA_PROJECT_KEY' not in st.session_state:
        st.session_state["ATLASSIAN_STATUS"] = False

    if 'ATLASSIAN_USER_ID' in st.secrets:
        st.session_state["ATLASSIAN_USER_ID"] = st.secrets['ATLASSIAN_USER_ID']
    elif 'ATLASSIAN_USER_ID' not in st.session_state:
        st.session_state["ATLASSIAN_STATUS"] = False

    if 'CONFLUENCE_SPACE_ID' in st.secrets:
        st.session_state["CONFLUENCE_SPACE_ID"] = st.secrets['CONFLUENCE_SPACE_ID']
    elif 'CONFLUENCE_SPACE_ID' not in st.session_state:
        st.session_state["ATLASSIAN_STATUS"] = False

    if st.session_state["ATLASSIAN_STATUS"]:
        st.session_state['JIRA_URL'] = "https://" + st.session_state['ATLASSIAN_DOMAIN'] + ".atlassian.net/rest/api"
        st.session_state['CONFLUENCE_URL'] = "https://" + st.session_state['ATLASSIAN_DOMAIN'] + ".atlassian.net/wiki/api"
        st.session_state['ATLASSIAN_HEADERS'] = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        st.session_state['AUTH'] = HTTPBasicAuth(username=st.session_state['ATLASSIAN_USER_NAME'],
                             password=st.session_state['ATLASSIAN_API_TOKEN'])