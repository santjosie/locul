import fitz
import io
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

    chunks = text_splitter.split(text)
    df = pd.DataFrame(chunks, columns=['chunks'])
    yield from df.itertuples(index=False, name=None)

def text_from_pdf(pdf_document):
    """
    Accepts a list of pdf files and extracts text from the files

    Parameters:
    pdf_document: pdf file as BytesIO stream

    Returns:
    stream: text content of pdf_document as BytesIO stream
    """
    for pdf in pdf_document:
        pdf_content = fitz.open(stream=pdf.read())
        stream = io.BytesIO()
        for page in pdf_content:
            page_content = page.get_text()
            stream.write(page_content.encode('utf-8'))
            stream.write(b'\n')
    return stream.getvalue().decode('utf-8')

def generate_documents(text: str):
    """
    Accepts a string and converts into a list of strings each about 1000 words in length

    Parameters:
    stream: text content as BytesIO stream

    Returns:
    documents: text content in stream converted into a list of strings with each item having up to 1000 words
    """
    documents = []
    words = text.split()
    chunk_size = 1000
    for i in range (0, len(words), chunk_size):
        documents.append(' '.join(words[i:i+chunk_size]))
    return documents
