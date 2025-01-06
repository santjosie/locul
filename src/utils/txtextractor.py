import pandas as pd
from langchain.text_splitter import RecursiveCharacterTextSplitter

def chunkerizer(text: str):
    """
    Accepts a string and splits it into chunks of 1512 characters with an overlap of 256 characters

    Parameters:
    text: string to be split into chunks

    Returns:
    df.itertuples: iterates through the chunks in the dataframe
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1512,
        chunk_overlap=256,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    df = pd.DataFrame(chunks, columns=['chunks'])
    return df.itertuples(index=False, name=None)

def