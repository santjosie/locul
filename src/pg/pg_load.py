import streamlit as st
from utils import txtextractor

def header():
    st.header('Load local history')
    st.caption('Upload historical records to Locul for analysis')

def upload_pdf():
    pdf_document = st.file_uploader(label='Upload historical documents'
                                    , accept_multiple_files=True
                                    , type=['pdf']
                                    , label_visibility='collapsed')

    if pdf_document:
        st.write('Processing historical records...')
        generate_embed = st.button(label='Load', type='primary',
                                   help='Once you have uploaded all the policy documents, click this button to load them to your Locul database.')
        if generate_embed:
            text_stream = txtextractor.text_from_pdf(pdf_document)
            documents = txtextractor.generate_documents(text_stream)

def body():
    header()
    upload_pdf()

body()