import os
import openai
from bs4 import BeautifulSoup, Comment
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = api_key

def identify_impacted_nodes(discrepancies, threshold=5.0):
    impacted_nodes = [node for node, normal_dist, impaired_dist in discrepancies if impaired_dist - normal_dist > threshold]
    return impacted_nodes

def generate_accessibility_suggestions(node_name):
    prompt = f"The HTML node <{node_name}> has shown significant changes in its attributes or position, affecting accessibility for visually impaired users. Suggest improvements to enhance its accessibility.The improvement should given the fixed node, should be in the form of an alt attribute for the image tag."
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
            # print(f"Applying suggestion to {node}: {suggestion}")  # Debug information
            print(f"Applying suggestion to {node} \n")  # Debug information

            if "alt=" in suggestion:
                print("ALTTTTTTT!!!!!!!!!!")  # Debugging print statement
                
                alt_text_start = suggestion.index('alt="') + len('alt="') 
                alt_text_end = suggestion.index('"', alt_text_start)
                alt_text = suggestion[alt_text_start:alt_text_end]
                node['alt'] = alt_text
                print(f"Added alt text to {node}: {alt_text}")  # Debug information
            
            if "role=" in suggestion:
                pass
            if "aria-label=" in suggestion:
                pass
            
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

# print("-------- Enhanced HTML Document --------")
# print(enhanced_html_doc)
