import streamlit as st
from utils import session as ses

def header():
    st.header("Configure Locul")
def content():
    model_tab, atlas_tab, prompt_tab = st.tabs(["Model", "Atlassian", "Prompt"])
    with model_tab:
        model_col, rag_col, def_col = st.columns(3, border=True)
        with model_col:
            st.subheader("Model")
            models = ['mixtral-8x7b',
                      'snowflake-arctic',
                      'mistral-large',
                      'llama3-8b',
                      'llama3-70b',
                      'reka-flash',
                      'mistral-7b',
                      'llama2-70b-chat',
                      'gemma-7b']
            st.session_state['MODEL'] = st.selectbox("Select model", options=models, index=2)
            st.session_state['TOP_P'] = st.slider(label="Top P", min_value=0.1, max_value=1.0, value=st.session_state['TOP_P'], step=0.1)
            st.session_state['TEMPERATURE'] = st.slider(label="Temperature", min_value=0.1, max_value=1.0, value=st.session_state['TEMPERATURE'],
                                                        step=0.1)
            st.session_state['MAX_TOKENS'] = st.slider(label="Max tokens", min_value=256, max_value=4096, value=st.session_state['MAX_TOKENS'],
                                                       step=256)

        with rag_col:
            st.subheader("RAG")
            st.session_state['NUM_CHUNKS'] = st.slider(label="Number of chunks", min_value=1, max_value=5, value=st.session_state['NUM_CHUNKS'], step=1)

    with atlas_tab:
        auth_col, jira_col, conf_col = st.columns(3, border=True)
        with auth_col:
            st.subheader("Atlassian")

            if 'ATLASSIAN_API_TOKEN' in st.session_state:
                st.text_input("API token", value=st.session_state['ATLASSIAN_API_TOKEN'], type="password")
            else:
                st.session_state['ATLASSIAN_API_TOKEN'] = st.text_input("API token", type="password")

            if 'ATLASSIAN_USER_NAME' in st.session_state:
                st.text_input("User name", value=st.session_state['ATLASSIAN_USER_NAME'])
            else:
                st.session_state['ATLASSIAN_USER_NAME'] = st.text_input("User name")

            if 'ATLASSIAN_DOMAIN' in st.session_state:
                st.text_input("Domain", value=st.session_state['ATLASSIAN_DOMAIN'])
            else:
                st.session_state['ATLASSIAN_DOMAIN'] = st.text_input("Domain")

            if 'ATLASSIAN_USER_ID' in st.session_state:
                st.text_input("User ID", value=st.session_state['ATLASSIAN_USER_ID'])
            else:
                st.session_state['ATLASSIAN_USER_ID'] = st.text_input("User ID")

        with jira_col:
            st.subheader("JIRA")
            if 'JIRA_PROJECT_KEY' in st.session_state:
                st.text_input("Project key", value=st.session_state['JIRA_PROJECT_KEY'])
            else:
                st.session_state['JIRA_PROJECT_KEY'] = st.text_input("Project key")

        with conf_col:
            st.subheader("Confluence")
            if 'CONFLUENCE_SPACE_ID' in st.session_state:
                st.text_input("Space ID", value=st.session_state['CONFLUENCE_SPACE_ID'])
            else:
                st.session_state['CONFLUENCE_SPACE_ID'] = st.text_input("Space ID")

    with prompt_tab:
        st.write("Prompt tab")

def main():
    ses.atlas_session()
    header()
    content()

main()