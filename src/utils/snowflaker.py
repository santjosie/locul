from snowflake.snowpark import Session
from snowflake.core import Root
import streamlit as st
import tempfile
import os

NUM_CHUNKS = 3

CONNECTION_PARAMETERS = {
   "account": st.secrets['SNOWFLAKE_ACCOUNT'],
   "user": st.secrets['SNOWFLAKE_USER'],
   "password": st.secrets['SNOWFLAKE_PASSWORD'],
 #  "role": "<your snowflake role>",  # optional
   "warehouse": st.secrets['SNOWFLAKE_WAREHOUSE'],  # optional
   "database": st.secrets['SNOWFLAKE_DB'],  # optional
   "schema": st.secrets['SNOWFLAKE_SCHEMA'],  # optional
   }

SESSION = Session.builder.configs(CONNECTION_PARAMETERS).create()

# service parameters
CORTEX_SEARCH_DATABASE = "LOCUL_DB"
CORTEX_SEARCH_SCHEMA = "LOCUL_SCHEMA"
CORTEX_SEARCH_SERVICE = "LOCUL_SEARCH_SERVICE"
STAGE_NAME = "LOCUL_DOCS"
root = Root(SESSION)
retrieval_search = root.databases[CORTEX_SEARCH_DATABASE].schemas[CORTEX_SEARCH_SCHEMA].cortex_search_services[CORTEX_SEARCH_SERVICE]
locul_stage = root.databases[CORTEX_SEARCH_DATABASE].schemas[CORTEX_SEARCH_SCHEMA].stages[STAGE_NAME]

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
                locul_stage.put(local_file_name=file_path,
                                stage_location="/",
                                auto_compress=False,
                                overwrite=True)
                file_names.append(file_name)
        except Exception as e:
            return 1, e

    return 0, file_names

def read_from_stage(file_name):
        try:
            with locul_stage.get(file_name) as file:
                text = file.read().decode('utf-8')
                chunks = snowflaker.generate_documents(text)
                for i, chunk in enumerate(chunks):
                    retrieval_search.put(chunk, file_name, i)
        except Exception as e:
            return 1, e
    return 0, None

def body():
    header()

if __name__ == "__main__":
    body()