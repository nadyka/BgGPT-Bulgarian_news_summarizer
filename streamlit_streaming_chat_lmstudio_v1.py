#### Streamlit Streaming Chatbot using LM Studio with OpenAI API Object Model 
#### Updated by Rich Lysakowski 2024.04.14
#### Original by Ingrid Stevens 2024.04.13
#### Streamlit Streaming using LM Studio as OpenAI Standin
#### run with `streamlit run app.py`

# !pip install pypdf langchain langchain-openai 

import os
from datetime import datetime
import json
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


# app config
st.set_page_config(page_title="LM Studio Streaming Chatbot", page_icon="🤖")
st.title("LM Studio Streaming Chatbot")

import os
import json
import streamlit as st
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate


# Add sidebar with buttons and input fields
st.sidebar.title("Chat Transcript Controls")
save_markdown = st.sidebar.button("Save Transcript as Markdown")
save_json = st.sidebar.button("Save Transcript as JSON")

base_name = st.sidebar.text_input("Base Name for Transcript Files", "chat_transcript")
chat_location = st.sidebar.text_input("Chat Location Folder", "./chat_location")

# Function to save transcript as Markdown
def save_transcript_as_markdown(chat_history, base_name, chat_location):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{base_name}_{timestamp}.md"
    file_path = os.path.join(chat_location, file_name)
    
    # Check if the folder exists and create it if not
    if not os.path.exists(chat_location):
        os.makedirs(chat_location)
        st.sidebar.info(f"Folder did not exist. Files saved to default location: {os.path.join(chat_location, base_name)}_{timestamp}.md")
    
    with open(file_path, "w", encoding="utf-8") as f:
        for i, message in enumerate(chat_history, start=1):
            if isinstance(message, AIMessage):
                f.write(f"### AI Message {i}\n\n{message.content}\n\n")
            elif isinstance(message, HumanMessage):
                f.write(f"### Human Message {i}\n\n{message.content}\n\n")

# Function to save transcript as JSON
def save_transcript_as_json(chat_history, base_name, chat_location):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{base_name}_{timestamp}.json"
    file_path = os.path.join(chat_location, file_name)
    
    # Check if the folder exists and create it if not
    if not os.path.exists(chat_location):
        os.makedirs(chat_location)
        st.sidebar.info(f"Folder did not exist. Files saved to default location: {os.path.join(chat_location, base_name)}_{timestamp}.json")
    
    transcript = []
    for i, message in enumerate(chat_history, start=1):
        if isinstance(message, AIMessage):
            transcript.append({"type": "AI", "message": message.content})
        elif isinstance(message, HumanMessage):
            transcript.append({"type": "Human", "message": message.content})
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(transcript, f, ensure_ascii=False, indent=4)

# Add sidebar with buttons for saving the chat transcript as Markdown and JSON files. 
# When a button is clicked, call the corresponding function to save transcript 
# with the specified base_name and chat_location.

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

if save_markdown:
    save_transcript_as_markdown(st.session_state.chat_history, base_name, chat_location)
    st.sidebar.success(f"Transcript saved as Markdown to {os.path.join(chat_location, base_name)}_{timestamp}.md")

if save_json:
    save_transcript_as_json(st.session_state.chat_history, base_name, chat_location)
    st.sidebar.success(f"Transcript saved as JSON to {os.path.join(chat_location, base_name)}_{timestamp}.json")


# The rest of your Streamlit application code goes here...

def get_response(user_query, chat_history):

    template = """
    You are a helpful assistant. Use the chat history if it helps, otherwise ignore it:

    Chat history: {chat_history}

    User response: {user_question}
    """

    prompt = ChatPromptTemplate.from_template(template)

    # Using LM Studio Local Inference Server
    #llm = ChatOpenAI(base_url="http://localhost:1234/v1")
    llm = ChatOpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

    chain = prompt | llm | StrOutputParser()
    
    return chain.stream({
        "chat_history": chat_history,
        "user_question": user_query,
    })

# session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content="Hello, I am a bot. How can I help you?"),
    ]

    
# conversation
for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.write(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.write(message.content)

# user input
user_query = st.chat_input("Type your message here...")
if user_query is not None and user_query != "":
    st.session_state.chat_history.append(HumanMessage(content=user_query))

    with st.chat_message("Human"):
        st.markdown(user_query)

    with st.chat_message("AI"):
        response = st.write_stream(get_response(user_query, st.session_state.chat_history))

    st.session_state.chat_history.append(AIMessage(content=response))
    
# Save the chat history to a markdown file with appropriate structure, metadata, and formatting
# if Markdown is involved, use the Markdown code block with section dividers, headers, bullet points or numbered lists as needed
# If Python code is involved, use the Python code block
# If JSON is involved, use the JSON code block
# If YAML is involved, use the YAML code block
# If SQL is involved, use the SQL code block
# If HTML is involved, use the HTML code block
# If XML is involved, use the XML code block
# If JavaScript is involved, use the JavaScript code block
# If CSS is involved, use the CSS code block
# If Bash is involved, use the Bash code block

#  