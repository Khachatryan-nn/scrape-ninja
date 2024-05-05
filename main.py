import subprocess
import streamlit as st
import google.generativeai as genai

from time import sleep
from urllib.parse import urlparse

genai.api_key = st.secrets.google.API_KEY_2
genai.configure(api_key=genai.api_key)

generation_config = {
  "temperature": 0,
  "top_p": 1,
  "top_k": 1,
  "max_output_tokens": 8192,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_ONLY_HIGH"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_ONLY_HIGH"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_ONLY_HIGH"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_ONLY_HIGH"
  }
]

model = genai.GenerativeModel(model_name= "gemini-1.5-pro-latest", # "gemini-1.0-pro-vision-latest", #"gemini-1.5-pro-latest",
                              generation_config=generation_config,
                              safety_settings=safety_settings)
model.timeout = 30

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
    """Search the provided Venture company's website for contact information.
Look for pages with titles or URLs containing keywords such as 'contact-us', 'contact', 'connect', 'connect-us', 'locations', or any other relevant terms that might indicate a page with contact information.
Extract and return the following information in JSON format:
- Company name
- Email addresses
- Phone numbers
- Physical addresses
- Contact forms (if available)""",

    """Search the provided Venture company's website for information about the industries they invest in.
Look for pages with titles or URLs containing keywords such as 'investment', 'industries','sectors', 'portfolio', or any other relevant terms that might indicate a page with investment information.
Extract and return the industries the company invests in, in JSON format.
If the information is not found on the company's website, search for relevant news articles or press releases that mention the company's investment industries.""",

    """Search the provided Venture company's website for information about their funding series.
Look for pages with titles or URLs containing keywords such as 'funding', 'investment','series', 'round', or any other relevant terms that might indicate a page with funding information.
Extract and return the series of funding (e.g., Series A, Series B, etc.) and the count of each series if available, in JSON format.
If the information is not found on the company's website, search for relevant news articles or press releases that mention the company's funding series.""",
]

conclusion_prompt = """Using the results from the previous three prompts, create a comprehensive JSON response that contains the following information:
- Contact information:
  - Email addresses
  - Phone numbers
  - Physical addresses
  - Contact forms (if available)
- Investment industries
- Funding series:
  - Series of funding (e.g., Series A, Series B, etc.)
  - Count of each series (if available)
Combine the extracted information into a single JSON response."""

model_responses = []
# Accept user input
if prompt := st.chat_input("Venture company or website: "):
    extracted_name = extract_website_name(prompt)
    company_name = extracted_name if extracted_name else prompt
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    for template in prompt_templates[0:1]:
        prompt = f"Company:{company_name}. {template}"
        # Display assistant response in chat message container
        process = subprocess.Popen(['node', 'web_agent.js', prompt], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        output, error = process.communicate()
        while process.poll() is None:
            sleep(0.1)
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
