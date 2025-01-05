import streamlit as st
from utils import txtextractor, snowflaker

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
            load_status, file_names = snowflaker.load_to_stage(pdf_document) #upload files to stage
            if load_status == 1:
                st.error(f'An error occurred while uploading the files to stage. {file_names}')
            else:
                for file_name in file_names:
                    parsed_text = snowflaker.read_from_stage(file_name) #parse text from doc storage
                    chunks = txtextractor.chunkerizer(parsed_text) #chunkerize
                    chunks_with_file = [(chunk[0], file_name) for chunk in chunks]
                    snowflaker.inser_chunks(chunks_with_file) #save_in_chunks_table

def body():
    header()
    upload_pdf()

body()