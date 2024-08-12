"""
Implement a function that would get an HTML file as input. It would generate two outputs in response. First output contains information available only to the visual users. We should remove all the classes, ids, etc, and only keep the text information. The other output contains the information available only to the visually impaired people. This information includes aria labels, alt text, etc, but all the other information (classes, ids, text information) must be removed. The process should be automatic and both outputs are describing a single HTML file, but with different attributes and values.
"""

import os
from bs4 import BeautifulSoup

# Function to extract information and generate the two outputs
def extract_information_from_html(html_content):
    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # First output: Only text information for visual users
    visual_content = soup.get_text(separator='\n', strip=True)
    
    # Second output: Only accessibility information (aria-labels, alt texts, etc.)
    accessibility_info = []
    
    # Extract aria-labels
    for tag in soup.find_all(attrs={"aria-label": True}):
        accessibility_info.append(tag['aria-label'])
    
    # Extract alt texts from images
    for img_tag in soup.find_all('img', alt=True):
        accessibility_info.append(img_tag['alt'])
    
    # Extract role attributes
    for tag in soup.find_all(attrs={"role": True}):
        role_info = f"Role: {tag['role']}"
        if 'aria-label' in tag.attrs:
            role_info += f", Label: {tag['aria-label']}"
        accessibility_info.append(role_info)

    # Extract aria-labelledby
    for tag in soup.find_all(attrs={"aria-labelledby": True}):
        label_id = tag['aria-labelledby']
        label_tag = soup.find(id=label_id)
        if label_tag:
            accessibility_info.append(f"Labelled by: {label_tag.get_text(separator=' ', strip=True)}")
    
    # Convert accessibility information to a single string
    accessibility_content = "\n".join(accessibility_info)
    
    return visual_content, accessibility_content

html_file_path = 'input/detailed_example.html' 
with open(html_file_path, 'r') as file:
    html_content = file.read()

# Get the two outputs
visual_output, accessibility_output = extract_information_from_html(html_content)

# Save the outputs to files
visual_output_path = 'output/visual_output.txt'
impaired_output_path = 'output/impaired_output.txt'

with open(visual_output_path, 'w') as file:
    file.write(visual_output)

with open(impaired_output_path, 'w') as file:
    file.write(accessibility_output)

# Return the paths of the generated files
# visual_output: A string containing all the text information available to visual users.
# accessibility_output: A string containing only the information available to visually impaired users, such as aria-label, alt text, and role descriptions.
visual_output_path, impaired_output_path
