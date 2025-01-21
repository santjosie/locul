# locul
AI assistant for Product Manages

Locul is an AI assistant for Product Managers that 
1. Automatically generates release notes for new features and bug fixes that are part of a version upgrade.
2. Acts as the first line of defence to answer any product-related questions from various stakeholders.

## How does it work?
Locul integrates with your software development project tracking tool, such as JIRA, identifies new user stories that have been certified and added to a release version, and automatically creates the first draft of release notes for your features.

Once you have reviewed these notes, and made changes as required, Locul takes the final draft of the release note and creates embeddings on the content to create a searchable knowledge database for your product.

Using Locul's chat interface, the various stakeholders you deal with can first ask Locul any questions about the product's functionality.

## What's under the hood?
Locul has been built using the Snowflake ecosystem. The programming language used is Python. The front end has been built using Streamlit. The data storage used is Snowflake. Snowflake Cortex's AI search service has been used to implement RAG.

## What's next for Locul
End-to-end AI agent for PMs. In a previous Snowflake hackathon, I built a tool, Hooser, that automatically generates user stories based on a prompt. I will merge Locul with Hooser to create an end-to-end more powerful and capable AI assistant for Product Managers, running on Snowflake and integrated with existing product management tools such as JIRA and Linear.
