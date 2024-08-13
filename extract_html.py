"""
Implement a function that would get an HTML file as input. It would generate two outputs in response. First output contains information available only to the visual users. We should remove all the classes, ids, etc, and only keep the text information. The other output contains the information available only to the visually impaired people. This information includes aria labels, alt text, etc, but all the other information (classes, ids, text information) must be removed. The process should be automatic and both outputs are describing a single HTML file, but with different attributes and values.
"""
import os
from bs4 import BeautifulSoup
import copy  # Import the copy module

# Function to generate two HTML outputs
def generate_accessible_html_outputs(html_content):
    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Create a deep copy for the impaired output
    impaired_soup = copy.deepcopy(soup)

    # Expanded list of attributes to remove for visual output
    accessibility_attrs = [
        'aria-label', 'role', 'aria-labelledby', 'aria-describedby',
        'aria-hidden', 'tabindex', 'alt', 'aria-controls', 'aria-expanded',
        'aria-pressed', 'aria-selected', 'aria-live', 'aria-atomic', 
        'aria-relevant', 'aria-busy', 'aria-disabled'
    ]

    # Process for visual output: Remove accessibility attributes
    for tag in soup.find_all(True):
        for attr in accessibility_attrs:
            if attr in tag.attrs:
                del tag[attr]

    # Process for impaired output: Keep only accessibility information
    for tag in impaired_soup.find_all(True):
        # If the tag does not have any accessibility attributes, remove its text content
        if not any(attr in tag.attrs for attr in accessibility_attrs):
            for child in tag.find_all(string=True):
                child.extract()  # This removes all text content from the tag
        
        # Only keep the accessibility attributes, remove everything else except tag structure
        tag.attrs = {k: v for k, v in tag.attrs.items() if k in accessibility_attrs}
    
    # Convert both soups back to HTML strings
    visual_output = soup.prettify()
    impaired_output = impaired_soup.prettify()

    return visual_output, impaired_output


# Example usage
html_file_path = 'input/detailed_example.html' 
with open(html_file_path, 'r') as file:
    html_content = file.read()

# Get the two outputs
visual_output, impaired_output = generate_accessible_html_outputs(html_content)

# Save the outputs to HTML files
visual_output_path = 'output/visual_output.html'
impaired_output_path = 'output/impaired_output.html'

with open(visual_output_path, 'w') as file:
    file.write(visual_output)

with open(impaired_output_path, 'w') as file:
    file.write(impaired_output)

# Return the paths of the generated files
visual_output_path, impaired_output_path
