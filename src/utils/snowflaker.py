from snowflake.snowpark import Session
from snowflake.core import Root
import streamlit as st
import tempfile
import os
import json

NUM_CHUNKS = 3

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
CORTEX_SEARCH_SERVICE = "locul_release_notes_search"
STAGE_NAME = "LOCUL_DOCS"

MODEL = 'mistral-large'
"""
         'mixtral-8x7b',
        'snowflake-arctic',
        'mistral-large',
        'llama3-8b',
        'llama3-70b',
        'reka-flash',
        'mistral-7b',
        'llama2-70b-chat',
        'gemma-7b'), key="model_name"))
"""

RETRIEVAL_SEARCH_SERVICE = ROOT.databases[CORTEX_SEARCH_DATABASE].schemas[CORTEX_SEARCH_SCHEMA].cortex_search_services[CORTEX_SEARCH_SERVICE]
LOCUL_STAGE = ROOT.databases[CORTEX_SEARCH_DATABASE].schemas[CORTEX_SEARCH_SCHEMA].stages[STAGE_NAME]

def header():
    st.header("Load local history")
    st.caption("Upload historical records to Locul for analysis")

def load_to_stage(files):
    file_names = []
    for file in files:
        try:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(file.getvalue())
                file_path = temp_file.name
                file_name = os.path.basename(file_path)
                LOCUL_STAGE.put(local_file_name=file_path,
                                stage_location="/",
                                auto_compress=False,
                                overwrite=True)
                file_names.append(file_name)
        except Exception as e:
            return 1, e
    return 0, file_names

def read_from_stage(file_name):
    df = SESSION.sql(f"""
            select 
                snowflake.cortex.parse_document('@{STAGE_NAME}', '{file_name}') as parsed_document
        """)

    row = df.collect() #assuming single row returned
    return json.loads(row[0]['PARSED_DOCUMENT']).get("content") #get the first row of dataframe, then convert to dict, then get value against content key

def insert_chunks(chunks):
    table_name = "locul_docs_chunks"
    df = SESSION.createDataFrame(chunks, schema=["chunk", "relative_path"])
    df.write.mode("append").saveAsTable(table_name)

def insert_release_chunks(chunks):
    table_name = "locul_release_chunks"
    df = SESSION.createDataFrame(chunks, schema=["key", "chunk", "title", "story_url", "notes_url"])
    df.write.mode("append").saveAsTable(table_name)

def complete_response(prompt):
    cmd = """
            select snowflake.cortex.complete(?, ?) as response
          """
    df_response = SESSION.sql(cmd, params=[MODEL, prompt]).collect()
    return df_response

def get_similar_chunks_search_service(query):
    columns = ["chunk", "title"]
    response = RETRIEVAL_SEARCH_SERVICE.search(query, columns, limit=NUM_CHUNKS)
    return response.json()

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
           You are an expert chat assistance that extracs information from the CONTEXT provided
           between <context> and </context> tags.
           When ansering the question contained between <question> and </question> tags
           be concise and do not hallucinate. 
           If you don´t have the information just say so.
           Only anwer the question if you can extract it from the CONTEXT provideed.
           
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