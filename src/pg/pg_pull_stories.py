import streamlit as st
from utils import atlassian as atlas

def header():
    st.header("Pull user stories")
    st.caption('Pull user stories from your ticket system to analyze them for insights.')

def pull_stories():
    pull = st.button(label='Pull stories', type='primary', help='Click this button to pull user stories from your ticket system.')
    if pull:
        atlas.get_unprocessed_issues()
        # get list of pulled stories
        # get list of stories that are not pulled
        # pull unpulled stories
        # put it through embedding

def body():
    header()
    pull_stories()

body()