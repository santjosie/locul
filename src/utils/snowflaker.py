from snowflake.snowpark import Session
from snowflake.core import Root
import streamlit as st
import tempfile
import os
import json
from utils import session as ses

ses.snowflake_session()

CONNECTION_PARAMETERS = {
   "account": st.secrets['SNOWFLAKE_ACCOUNT'],
   "user": st.secrets['SNOWFLAKE_USER'],
   "password": st.secrets['SNOWFLAKE_PASSWORD'],
   "warehouse": st.secrets['SNOWFLAKE_WAREHOUSE'],  # optional
   "database": st.secrets['SNOWFLAKE_DB'],  # optional
   "schema": st.secrets['SNOWFLAKE_SCHEMA'],  # optional
   }

SESSION = Session.builder.configs(CONNECTION_PARAMETERS).create()
ROOT = Root(SESSION)

# service parameters
CORTEX_SEARCH_DATABASE = "LOCUL_DB"
CORTEX_SEARCH_SCHEMA = "LOCUL_SCHEMA"
CORTEX_SEARCH_SERVICE = "locul_search_service"
STAGE_NAME = "LOCUL_DOCS"

MODEL = 'mistral-large'

RETRIEVAL_SEARCH_SERVICE = ROOT.databases[CORTEX_SEARCH_DATABASE].schemas[CORTEX_SEARCH_SCHEMA].cortex_search_services[CORTEX_SEARCH_SERVICE]

def insert_release_chunks(chunks):
    table_name = "locul_release_chunks"
    df = SESSION.createDataFrame(chunks, schema=[ "chunk", "title"])
    df.write.mode("append").saveAsTable(table_name)

def complete_response(prompt):
    cmd = """
            select snowflake.cortex.complete(?, ?) as response
          """
    df_response = SESSION.sql(cmd, params=[st.session_state['MODEL'], prompt]).collect()
    return df_response[0].RESPONSE

def get_similar_chunks_search_service(query):
    columns = ["chunk", "title"]
    response = RETRIEVAL_SEARCH_SERVICE.search(query, columns, limit=st.session_state['NUM_CHUNKS'])
    return json.loads(response.json())['results']

def release_note_prompt(story):

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

def knowledge_base_prompt(question, context):

    prompt = f"""
           You are an expert chat assistance that extracts information from the CONTEXT provided
           between <context> and </context> tags.
           When answering the question contained between <question> and </question> tags
           be concise and do not hallucinate. 
           If you don´t have the information just say so.
           Only answer the question if you can extract it from the CONTEXT provided.
           
           Do not mention the CONTEXT used in your answer.
    
           <context>          
           {context}
           </context>
           <question>  
           {question}
           </question>
           Answer: 
           """

    return prompt


def user_story_prompt(context, features):
    prompt = f"""
            You are a seasoned product manager. You are an expert in writing detailed user stories, which are used
            by designers and developers to build new features in your product. Your task is to create user stories
            for new features and requirements that are provided to you by the user. The requirements are extracted
            from the CONTEXT provided between <context> and </context> tags.
            
            After understanding the requirements, you need to consider features in the existing product that are related to
            the new feature that you are building. These are provided between the <features> and </features> tags.
            The new user story should attempt to design the new feature in the context of the existing features.
    
            The user story should contain the following sections, the title of each section is specified between the <title>
             and </title> tags and the instruction for what to write in each section is specified between the <instruction>
             and </instruction> tags.
            
            <title>Title</title>
            <instructions>This is a short sentence that describes the user story. Written from the perspective of the user
            and what their needs are. The format in which it needs to be written is [User] [verb] [what they are doing].
            Example - Recruiter updates the status of a ticket</instructions>
            
            <title>Oneliner</title>
            <instructions>Do not show the heading for this section. An expansion on the title, giving a bit more information
            regarding the goals of the user. Also written from the perspective of the user. Can introduce the context.
            Focus is on the final need of the user that needs to be achieved in the specified setting.
            The format in which it needs to be written is "As a [User], I want to [action they want to take], so that
            [why they want to take that action].
            Example - As a recruiter, I want to update the status of a ticket that I am working on so that the candidate
            is informed of the current status of the ticket.</instructions>
            
            <title>Process flow</title>
            <instructions>A numbered list depicting each user interaction and system responses in the user flow.</instructions>"
            
            <title>Specifications</title>
            <instructions>While the core of the user story focuses on the user and their primary need, the user story
            issue also needs to contain mandatory specifications if any. These could include information about the
            specific capabilities that need to be supported - for instance, ability to add and edit information, but
            prevent the deletion of information. Use Crisp writing style when adding this information in. Any formulas
            for calculation of values, behaviour of page on interactions etc. should be specified here.</instructions>
            
            <title>Acceptance criteria</title>
            <instructions>These are all the minimum scenarios that need to be tested after the feature has been built.
            Each acceptance criteria should be written in in Gherkin format, that is in the Given...When...Then.. format.
            In this format, under the Given section, you will describe the setup data for the scenario, the When section
            will describe the action or even that initiates the scenario, and the Then section will describe the desired
            outcome or result.</instructions>
            
            Use simple language. Keep sentences short. Avoid redundancy. Limit adjectives and adverbs. Make sure that you
            cover all the edge cases and complex scenarios when creating user stories and the acceptance criteria.

           <context>          
           {context}
           </context>
           
           <features>
           {features}
           </features>
           
           Do not mention the CONTEXT used in your answer.
           
           User story: 
           """

    return prompt

