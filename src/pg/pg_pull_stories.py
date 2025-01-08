import streamlit as st
from utils import atlassian as atlas
from utils import snowflaker, txtextractor

def header():
    st.header("Locul")
    st.caption('Locul is an AI agent assistant for product managers and technical writers. Use Locul to auto-generate release notes from your user stories and then create a searchable knowledge base for your product.')
    st.divider()

def create_prompt(story):

    prompt = f"""
           You are an expert at creating release notes for user stories contained within the CONTEXT provided
           between <context> and </context> tags.
           When creating release notes, be concise and do not hallucinate. 

           Do not mention the CONTEXT used in your answer.

           <context>          
           {story}
           </context>
           Release notes: 
           """

    return prompt

def complete(story):
    prompt = create_prompt(story)
    df_response = snowflaker.complete_response(prompt)
    return df_response

def pull_stories():
    pull = st.button(label='Pull stories', type='primary', help='Click this button to pull user stories from your ticket system.')
    if pull:
        stories = atlas.get_unprocessed_issues()  # pull unpulled stories in release version @TODO - add release version parameter
        if stories:
            for story in stories:
                jira_response = complete(story['summary'] + " "+ story['description']) #got the release note
                release_note = jira_response[0].RESPONSE #parsed release note
                confluence_response = atlas.write_to_confluence(story['key'] + ": " + story['summary'], release_note) #write to confluence
                st.write(confluence_response)
                confluence_web_link = confluence_response['_links']['base'] + confluence_response['_links']['webui'] #get confluence web link
                jira_web_link = "https://" + atlas.ATLASSIAN_DOMAIN + ".atlassian.net/browse/" + story['key']
                chunks = txtextractor.chunkerizer(release_note) #chunkify the release note
                st.write(chunks)
                chunks_with_metadata = [(story['key'], chunk[0], story['summary'], jira_web_link, confluence_web_link) for chunk in chunks] #create list with chunk and metadata of chunk (jira issue key, user story title, release note url, jira url)  @TODO
                st.write(chunks_with_metadata)
                snowflaker.insert_release_chunks(chunks_with_metadata) #save_in_chunks_table#push the chunks into snowflake @TODO

def content():
    issues_col, notes_col, base_col = st.columns(3)
    with issues_col:
        st.subheader("New features")
        with st.container(border=True):
            st.write("Temporary placeholder")
            """stories = atlas.get_unprocessed_issues()
            for story in stories:
                with st.expander(story['summary'], expanded=False):
                    st.markdown(story['description'])"""

    with notes_col:
        st.subheader("Release notes")
        with st.container(border=True):
            st.write("Temporary placeholder")
            #st.table(data=atlas.get_release_notes())

    with base_col:
        st.subheader("Kowledge base")
        with st.container(border=True):
            question = st.text_input("Ask question's about your product's functionality",
                                     placeholder="How does an employee book a vacation?")

            if question:
                prompt_context = snowflaker.get_similar_chunks_search_service(question)
                answer = snowflaker.complete(prompt_context)

    #user stories available for processing

def body():
    header()
    content()
    #pull_stories()

body()