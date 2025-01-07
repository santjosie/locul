import streamlit as st
from utils import atlassian as atlas
from utils import snowflaker

def header():
    st.header("Pull user stories")
    st.caption('Pull user stories from your ticket system to analyze them for insights.')

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
                response = complete(story) #got the release note
                res_text = response[0].RESPONSE #parsed release note
                st.markdown(res_text) #create confluence page for the release note
                st.write(response)
        #generate release notes
        # put it through embedding

def body():
    header()
    pull_stories()

body()