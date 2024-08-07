import openai
import os
import base64
import requests
from bs4 import BeautifulSoup, Comment
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

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
        "model": "gpt-4",
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
    
    if response.status_code != 200:
        print(f"Error: Received status code {response.status_code} from OpenAI API")
        print(f"Response: {response.text}")
        return "Image description not available"

    response_json = response.json()
    if "choices" not in response_json or not response_json["choices"]:
        print("Error: No choices found in the response")
        return "Image description not available"

    detailed_alt_text = response_json["choices"][0].get("message", {}).get("content", "").strip()
    return detailed_alt_text

def identify_impacted_nodes(discrepancies, threshold=5.0):
    impacted_nodes = [node for node, normal_dist, impaired_dist in discrepancies if impaired_dist - normal_dist > threshold]
    return impacted_nodes

def generate_accessibility_suggestions(node_name):
    prompt = f"The HTML node <{node_name}> has shown significant changes in its attributes or position, affecting accessibility for visually impaired users. Suggest improvements to enhance its accessibility. The improvement should be given the fixed node, should be in the form of an alt attribute for the image tag. The alt attribute should describe the image content in a concise and informative manner."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=100
    )
    suggestions = response.choices[0].message['content'].strip()
    return suggestions

def apply_suggestions_to_html(html_doc, suggestions, output_file_path):
    soup = BeautifulSoup(html_doc, 'html.parser')
    for node_name, suggestion in suggestions.items():
        print(f"Processing node: {node_name}")  # Debug information
        node_id = node_name.split("_")[0]
        node_id_value = node_name.split("_")[1]
        nodes = soup.find_all(node_id, id=node_id_value) if node_id_value else soup.find_all(node_id)

        for node in nodes:
            if node.name == 'img' and 'src' in node.attrs:
                print("Generating detailed alt text...")  # Debugging print statement
                image_path = node['src']
                detailed_alt_text = generate_detailed_alt_text(image_path)
                node['alt'] = detailed_alt_text
                print(f"Added alt text to {node}: {detailed_alt_text}")  # Debug information
                
        print("--------------------------------------------------------")

    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(str(soup))

# Example discrepancies output
discrepancies = [
    ("address_contact_", 2.18, 20.73),
    ("img_", 1.5, 15.8),  # Added discrepancy for img to demonstrate alt text addition
]

# Identify impacted nodes
impacted_nodes = identify_impacted_nodes(discrepancies)

# Generate suggestions
suggestions = {}
for node in impacted_nodes:
    suggestion = generate_accessibility_suggestions(node)
    suggestions[node] = suggestion

# Print suggestions
for node, suggestion in suggestions.items():
    print(f"Node: {node}\nSuggestion: {suggestion}\n")

# More problematic impaired HTML document
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

# Apply the suggestions to the HTML
output_file_path = 'enhanced_document.html'
apply_suggestions_to_html(impaired_html_doc, suggestions, output_file_path)

# Print the enhanced HTML
with open(output_file_path, 'r', encoding='utf-8') as file:
    enhanced_html_doc = file.read()

print(enhanced_html_doc)
