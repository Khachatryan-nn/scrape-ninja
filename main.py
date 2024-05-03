import streamlit as st
from transformers import AutoModelForCausalLM, AutoTokenizer

# Load your LLM chatbot model
# model_name = "meta-llama/Meta-Llama-3-8B"
# model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True)
# tokenizer = AutoTokenizer.from_pretrained(model_name)

# Create a chat panel in the center of the page
chat_panel = st.container()

# Create an input field at the bottom of the page
input_field = st.text_input("Type a message:")

# Initialize the conversation history
conversation_history = []

# Define a function to generate a response from the model
def generate_response(input_text):
#     inputs = tokenizer.encode_plus(input_text, 
#                                     add_special_tokens=True, 
#                                     max_length=1024, 
#                                     return_attention_mask=True, 
#                                     return_tensors='pt')
#     outputs = model(inputs['input_ids'], attention_mask=inputs['attention_mask'])
#     response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response

# # Define a function to update the conversation history
def update_conversation_history(input_text, response):
#     conversation_history.append({"user": input_text, "assistant": response})
    chat_panel.write("User: " + input_text + "\nAssistant: " + response + "\n")

# Create a button to submit the input
submit_button = st.button("Send")

# Handle the input submission
if submit_button:
    # input_text = input_field.value
    input_text = input_field
    # response = generate_response(input_text)
    response = "Hello!"
    update_conversation_history(input_text, response)
    input_field = ""

# Display the conversation history
chat_panel.write("Conversation History:")
for message in conversation_history:
    chat_panel.write("User: " + message["user"] + "\nAssistant: " + message["assistant"] + "\n")
