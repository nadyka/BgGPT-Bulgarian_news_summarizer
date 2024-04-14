import streamlit as st
from lmstudio import LMstudioClient

# Create a client to the LMstudio server
client = LMstudioClient(host="localhost", port=8080)

# Define a function to generate text
def generate_text(prompt):
    response = client.generate(prompt)
    return response.text

# Create a Streamlit app
st.title("LMstudio Text Generator")

# Get the user's prompt
prompt = st.text_input("Enter a prompt:")

# Generate text
text = generate_text(prompt)

# Display the generated text
st.write(text)
