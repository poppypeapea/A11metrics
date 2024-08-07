# Learn how to use vision capabilities to understand images.

import openai
import os
import base64
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def generate_detailed_alt_text(image_path):
    base64_image = encode_image(image_path)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai.api_key}"
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "What’s in this image?"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    detailed_alt_text = response.json().get("choices")[0].get("message").get("content").strip()
    return detailed_alt_text

def apply_suggestions_to_html(html_doc, output_file_path):
    soup = BeautifulSoup(html_doc, 'html.parser')
    img_tags = soup.find_all('img')

    for img in img_tags:
        if 'alt' not in img.attrs or not img.attrs['alt']:
            image_path = img['src']  # Assumes local file path, adjust if necessary for URL
            detailed_alt_text = generate_detailed_alt_text(image_path)
            img['alt'] = detailed_alt_text
    
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(str(soup))

# Example HTML document with an image
impaired_html_doc = """
<!DOCTYPE html>
<html>
<head>
    <title>Sample Impaired Document</title>
    <style>
        body { font-size: small; }
        h1 { color: red; }
    </style>
</head>
<body>
    <header>
        <h1>Welcome</h1>
    </header>
    <main id="main_content">
        <section>
            <h2>About</h2>
            <p>This is a sample website with minimal information.</p>
            <img src="animals.jpg">
        </section>
    </main>
    <footer>
        <address id="contact">
            <p>Contact us at info@example.com</p>
        </address>
    </footer>
</body>
</html>
"""

output_file_path = 'enhanced_document.html'
apply_suggestions_to_html(impaired_html_doc, output_file_path)

# Print the enhanced HTML
with open(output_file_path, 'r', encoding='utf-8') as file:
    enhanced_html_doc = file.read()

print(enhanced_html_doc)
