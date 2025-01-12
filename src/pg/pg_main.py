import streamlit as st
from utils import atlassian as atlas
from utils import snowflaker, txtextractor, session as ses

def header():
    st.header("Locul")
    st.caption('Locul is an AI agent assistant for product managers and technical writers. Use Locul to auto-generate release notes from your user stories and then create a searchable knowledge base for your product.')


def pull_stories():
    pull_stories_text = "Pulling user stories..."
    pull_stories_bar = st.sidebar.progress(value=0, text=pull_stories_text)
    gen_notes_text = "Drafting release notes..."
    gen_notes_bar = st.sidebar.progress(value=0, text=gen_notes_text)
    pub_notes_text = "Publishing release notes..."
    pub_notes_bar = st.sidebar.progress(value=0, text=pub_notes_text)
    stories = atlas.get_unprocessed_issues()  # pull unpulled stories in release version @TODO - add release version parameter
    pull_stories_bar.progress(value=100, text=pull_stories_text)
    total_stories = len(stories)
    if stories:
        for i, story in enumerate(stories):
            prompt = snowflaker.release_note_prompt(story['summary'] + " "+ story['description'])
            release_note = snowflaker.complete_response(prompt) #got the release note
            gen_notes_bar.progress(value=((i+1)/total_stories), text=gen_notes_text)
            confluence_response = atlas.write_to_confluence(story['key'] + ": " + story['summary'], release_note) #write to confluence
            pub_notes_bar.progress(value=((i+1)/total_stories), text=pub_notes_text)
    st.sidebar.success("Release notes created and published", icon='😍')

def knowledge_base_creator():
    pull_notes_text = "Pulling release notes..."
    pull_notes_bar = st.sidebar.progress(value=0, text=pull_notes_text)
    chunk_notes_text = "Creating content chunks..."
    chunk_notes_bar = st.sidebar.progress(value=0, text=chunk_notes_text)
    metadata_notes_text = "Adding metadata to chunks..."
    metadata_notes_bar = st.sidebar.progress(value=0, text=metadata_notes_text)
    push_notes_text = "Pushing chunks..."
    push_notes_bar = st.sidebar.progress(value=0, text=push_notes_text)
    notes = atlas.get_release_notes()
    pull_notes_bar.progress(value=100, text=pull_notes_text)
    total_notes = len(notes)
    for i, note in enumerate(notes):
        chunks = txtextractor.chunkerizer(note['body']) #chunkify the release note @TODO - clean it up
        chunk_notes_bar.progress(value=((i + 1) / total_notes), text=chunk_notes_text)
        chunks_with_metadata = [(chunk[0], note['title']) for chunk in chunks] #create list with chunk and metadata of chunk   @TODO
        metadata_notes_bar.progress(value=((i + 1) / total_notes), text=metadata_notes_text)
        snowflaker.insert_release_chunks(chunks_with_metadata) #save_in_chunks_table @TODO
        push_notes_bar.progress(value=((i + 1) / total_notes), text=push_notes_text)
    st.sidebar.success("Release notes loaded to knowledge base", icon='😍')

def content():
    stories_tab, notes_tab, base_col, feature_col = st.tabs(["User stories", "Release notes", "Knowledge base", "New feature"])
    with stories_tab:
        if st.session_state['ATLASSIAN_STATUS']:
            st.caption("Below is the list of user stories that have been included in your new version drop.")
            create_notes = st.button("Create release notes", help="Click this button to generate release notes for the user stories.")
            if create_notes:
                pull_stories()
            st.subheader("List of user stories")
            with st.container(border=True):
                stories = atlas.get_unprocessed_issues()
                for story in stories:
                    with st.expander(story['summary'], expanded=False):
                        st.markdown(story['description'])
        else:
            st.info("Atlassian integration not configured. Enter details in the configuration page")

    with notes_tab:
        if st.session_state['ATLASSIAN_STATUS']:
            st.caption("Below is the list of release notes that have been generated for your new features")
            create_knowledge = st.button("Create knowledge base", help="Click this button to generate a knowledge base from your release notes.")
            if create_knowledge:
                knowledge_base_creator()
            st.subheader("Release notes")
            with st.container(border=True):
                releases = atlas.get_release_notes()
                for release in releases:
                    with st.expander(release['title'], expanded=False):
                        st.markdown(release['body'])
        else:
            st.info("Atlassian integration not configured. Enter details in the configuration page")

    with base_col:
        st.subheader("Knowledge base")
        with st.container(border=True):
            question = st.text_input("Ask question's about your product's functionality",
                                     placeholder="How does an employee book a vacation?")

            if question:
                prompt_context = snowflaker.get_similar_chunks_search_service(question)
                prompt = snowflaker.knowledge_base_prompt(question, prompt_context)
                answer = snowflaker.complete_response(prompt)
                st.write(answer)

    with feature_col:
        st.subheader("New feature")
        uploaded_file = st.file_uploader(label="Choose a file", label_visibility="collapsed", accept_multiple_files=True,
                                     type=["pdf", "docx", "doc", "txt"])
        if uploaded_file:
            generate = st.button("Generate user stories", type="primary")
            if generate:
                requirements_text = txtextractor.extract_text(uploaded_file)
                existing_features = snowflaker.get_similar_chunks_search_service(requirements_text)
                prompt = snowflaker.user_story_prompt(requirements_text, existing_features)
                user_stories = snowflaker.complete_response(prompt)
                st.markdown(user_stories)

def body():
    ses.atlas_session()
    header()
    content()

body()