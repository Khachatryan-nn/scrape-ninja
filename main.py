import subprocess
import tempfile
import os
import streamlit as st
from vision_scraper import *

API_KEY = st.secrets.google.API_KEY_1

st.set_page_config(
   page_title="Ex-stream-ly Cool App",
   page_icon="🧊",
   layout="wide",
   initial_sidebar_state="expanded",
)

chat_panel = st.container()
input_field = st.text_input("Type a message:")

conversation_history = []

def generate_response(input_text):
    # Placeholder response, you can replace this with your actual response generation logic
    response = "This is a generated response based on your input: " + input_text
    return response

def update_conversation_history(input_text, response):
    conversation_history.append({"user": input_text, "assistant": response})
    chat_panel.write("User: " + input_text + "\nAssistant: " + response + "\n")

def run_web_agent(input_text):
    process = subprocess.Popen(['node', 'web_agent.js'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    input_text_bytes = input_text.encode()
    stdout, stderr = process.communicate(input=input_text_bytes)

    if stderr:
        return "Error: " + stderr.decode()
    else:
        return stdout.decode()

# Create a button to submit the input
submit_button = st.button("Send")

# Handle the input submission
if submit_button:
    input_text = input_field

    # Run the web agent and capture its output
    web_agent_output = run_web_agent(input_text)

    # Update the conversation history
    update_conversation_history(input_text, web_agent_output)

    # Clear the input field
    input_field = ""

# Display the conversation history
chat_panel.write("Conversation History:")
for message in conversation_history:
    chat_panel.write("User: " + message["user"] + "\nAssistant: " + message["assistant"] + "\n")