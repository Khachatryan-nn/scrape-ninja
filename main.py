import subprocess
import streamlit as st

from time import sleep
from urllib.parse import urlparse

def extract_website_name(input_string):
    parsed_url = urlparse(input_string)
    website_name = parsed_url.netloc.split(".")[0]
    if website_name == "www":
        website_name = parsed_url.netloc.split(".")[1]
    return website_name

st.set_page_config(
   page_title="Ninja Scraper",
   page_icon="🕸️",
   layout="wide",
   initial_sidebar_state="expanded",
)

# Set a default model
if "genai_model" not in st.session_state:
    st.session_state["genai_model"] = "gemini-1.5-pro-latest"

st.session_state['messages'] = [{'role': 'assistant', 'content': 'Hello, welcome to the Ninja Scraper! How can I assist you today?'}]

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt_templates = [
    """Search provided Venture company for contact information.
    Look for pages with titles or URLs containing keywords such as 'contact-us', 'contact', 'connect', 'connect-us', 'locations', or any other relevant terms that might indicate a page with contact information.
    If found out what requested, respond strictly with the requested information, surely formatted in the JSON format.
    Extract and return any email addresses, phone numbers, physical addresses, or contact forms found on these pages.""",

    """Search provided Venture company for information about the industries they invest in.
    Look for pages with titles or URLs containing keywords such as 'investment', 'industries', 'sectors', 'portfolio', or any other relevant terms that might indicate a page with investment information.
    If found out what requested, respond strictly with the requested information, surely formatted in the JSON format.
    Extract and return the industries the company invests in. If the information is not found on the company's website, search for relevant news articles or press releases that mention the company's investment industries.""",

    """Search provided Venture company for information about their funding series.
    Look for pages with titles or URLs containing keywords such as 'funding', 'investment', 'series', 'round', or any other relevant terms that might indicate a page with funding information.
    Extract and return the series of funding (e.g., Series A, Series B, etc.) and the count of each series if available.
    If found out what requested, respond strictly with the requested information, surely formatted in the JSON format.
    If the information is not found on the company's website, search for relevant news articles or press releases that mention the company's funding series."""
]

# Accept user input
if prompt := st.chat_input("Venture company or website: "):
    extracted_name = extract_website_name(prompt)
    company_name = extracted_name if extracted_name else prompt
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    for template in prompt_templates:

        prompt = f"Company:{company_name}. {template}"
        # Display assistant response in chat message container
        process = subprocess.Popen(['node', 'web_agent.js', prompt], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        output, error = process.communicate()
        while process.poll() is None:
            sleep(0.1)
        with st.chat_message("assistant"):
            stream = output.decode().strip()
            response = st.write(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})