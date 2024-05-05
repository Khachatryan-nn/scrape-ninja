import streamlit as st
import subprocess
import google.generativeai as genai
from time import sleep
from urllib.parse import urlparse

from prompts import *

# Set API key and configure GenAI
genai.api_key = st.secrets.google.API_KEY_2
genai.configure(api_key=genai.api_key)

# Load the database as string
with open(".data/.data.json", "r") as f:
    database = f.read()

# Define generation config and safety settings
generation_config = {
    "temperature": 0,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 8192,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
]

# Define model and timeout
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-latest",
    generation_config=generation_config,
    safety_settings=safety_settings,
)
model.timeout = 30

# Define function to extract website name from input string
def extract_website_name(input_string):
    parsed_url = urlparse(input_string)
    website_name = parsed_url.netloc.split(".")[0]
    if website_name == "www":
        website_name = parsed_url.netloc.split(".")[1]
    return website_name

# Set page config
st.set_page_config(
    page_title="Ninja Scraper",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.session_state['messages'] = [{'role': 'assistant', 'content': 'Hello, welcome to the Ninja Scraper! How can I assist you today?'}]

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Venture company or website: "):
    extracted_name = extract_website_name(prompt)
    company_name = extracted_name if extracted_name else prompt

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    model_responses = []
    for template in prompt_templates[0:1]:
        prompt = f"Company:{company_name}. {template}"
        # Display assistant response in chat message container

        with st.spinner('Wait for it...'):
            process = subprocess.Popen(['node', 'web_agent.js', prompt], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            output, error = process.communicate()
            while process.poll() is None:
                sleep(0.2)

        with st.chat_message("assistant"):
            stream = output.decode().strip()
            response = st.write(stream)
            model_responses.append(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})

    # Make conclusion
    prompt = f"""{conclusion_prompt}
    {'    '.join(model_responses)}"""
    try:
        conclusion_response = model.generate_content(prompt,
                                                     generation_config=generation_config,
                                                     safety_settings=safety_settings,
                                                     stream=False)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(conclusion_response.text)

    except Exception as e:
        st.error(f"The ASSISTANT had an error: {e}")

    # Return most similar ones
    prompt = similarity_prompt.format(company_name, conclusion_response.text, database)

    try:
        similarity_response = model.generate_content(prompt,
                                                     generation_config=generation_config,
                                                     safety_settings=safety_settings,
                                                     stream=False)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(similarity_response.text)

    except Exception as e:
        st.error(f"The ASSISTANT had an error: {e}")