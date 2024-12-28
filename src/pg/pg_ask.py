import streamlit as st


def header():
    """Displays the header section on the Ask Locul page.

    """

    st.header("Ask Locul")
    st.caption('I am your local historian. Ask me anything you would love to know about your city.')

def input_prompt():
    """Displays the input field where the user will enter a prompt to generate the user story.

    """
    with st.container():
        # this is the input field where the user will enter a prompt to generate the user story
        prompt = st.chat_input(placeholder='What was the first passenger ship to dock at the Cochin port?')

        if prompt:
            st.write("Searching repositories for information on: ", prompt)
            st.write("Generating response...")
            st.write("Here you go!")


def body():
    header()
    input_prompt()

body()