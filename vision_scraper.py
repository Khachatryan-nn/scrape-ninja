import streamlit as st
import subprocess
import base64
import os

from PIL import Image
from dotenv import load_dotenv
from time import sleep

import google.generativeai as genai

load_dotenv()

API_KEY = st.secrets.google.API_KEY_2
SLEEP_TIME = int(os.getenv('SLEEP_TIME'))/1000 if os.getenv('SLEEP_TIME') else 0

genai.configure(api_key=API_KEY)

# Set up the model
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

def image_b64(image):
    with open(image, "rb") as f:
        return base64.b64encode(f.read()).decode()

def url2screenshot(url):
    print(f"Crawling the following link: {url}")

    if os.path.exists("screenshot.jpg"):
        os.remove("screenshot.jpg")

    result = subprocess.run(
        ["node", "screenshot.js", url],
        capture_output=True,
        text=True
    )

    exitcode = result.returncode
    output = result.stdout

    if not os.path.exists("screenshot.jpg"):
        print("ERROR: Image path doesn't exist!")
        return "Failed to scrape the website"
    
    #b64_image = image_b64("screenshot.jpg")
    #return b64_image
    return "screenshot.jpg"

def visionExtract(b64_image, prompt, image):
    sleep (SLEEP_TIME)
    response = model.generate_content([
        "You are a web scraper, your job is to extract information based on a screenshot of a website & user's instruction",
        prompt,
        Image.open(image),
	])
    
    message_text = response.candidates[0].content.parts[0].text

    if "ANSWER_NOT_FOUND" in message_text:
        print("ERROR: Answer not found")
        return "I was unable to find the answer on that website. Please pick another one"
    else:
        print(f"GPT: {message_text}")
        return message_text

def visionCrawl(url, prompt):
    b64_image = url2screenshot(url)
    #image_name = url2screenshot(url)

    
    if b64_image == "Failed to scrape the website":
        return "I was unable to crawl that site. Please pick a different one. Thanks!"
    else:
        print("Image captured")
        return visionExtract(b64_image, prompt, b64_image)

# response = visionCrawl("indexventures", "Extract the contact info")
# print(response)