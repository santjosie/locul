import streamlit as st
import pandas as pd
from langchain.text_splitter import RecursiveCharacterTextSplitter
from utils import session as ses
import PyPDF2
import docx2txt

def chunkerizer(text: str):
    """
    Accepts a string and splits it into chunks of 1512 characters with an overlap of 256 characters

    Parameters:
    text: string to be split into chunks

    Returns:
    df.itertuples: iterates through the chunks in the dataframe
    """
    ses.chunk_session()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = st.session_state['CHUNK_SIZE'],
        chunk_overlap = st.session_state['CHUNK_OVERLAP'],
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    df = pd.DataFrame(chunks, columns=['chunks'])
    return df.itertuples(index=False, name=None)

def extract_text(docs):
    full_text=""
    for doc in docs:
        if doc.type == "application/pdf":
            reader = PyPDF2.PdfReader(doc)
            text = ""
            for page in range(len(reader.pages)):
                text += reader.pages[page].extract_text()
        elif doc.type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
            text = docx2txt.process(doc)
        else:
            text = doc.read().decode("utf-8")
        full_text += text
    return full_text