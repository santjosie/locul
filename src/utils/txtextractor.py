import fitz
import io

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
    return stream

def generate_documents(stream):
    """
    Accepts a string and converts into a list of strings each about 1000 words in length

    Parameters:
    stream: text content as BytesIO stream

    Returns:
    documents: text content in stream converted into a list of strings with each item having up to 1000 words
    """
    documents = []
    words = stream.getvalue().decode('utf-8').split()
    chunk_size = 1000
    for i in range (0, len(words), chunk_size):
        documents.append(' '.join(words[i:i+chunk_size]))
    return documents
