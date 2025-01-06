import streamlit as st

def navigation():
    pages = [st.Page(page="pg/pg_ask.py", title="Ask Locul"),
             st.Page(page="pg/pg_pull_stories.py", title="Pull user stories"),
             st.Page(page="pg/pg_load.py", title="Load History"),
             st.Page(page="pg/pg_config.py", title="Configuration")]

    pg = st.navigation(pages=pages, expanded=True)
    pg.run()

def body():
    st.set_page_config(
        page_title='Locul | Home',
       # page_icon="assets/img/locul_logo.png",
        layout='wide',
        menu_items={
            'Get help': 'https://www.santhoshjose.dev',
            'About': '# Version: 1.0 #'
        })
    navigation()

if __name__ == '__main__':
    body()