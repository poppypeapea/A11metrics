import os
import requests
from bs4 import BeautifulSoup
import copy

# Function to fetch HTML content from a website
def fetch_website_html(url):
    response = requests.get(url)
    if response.status_code == 200:
        print("Successfully fetched the webpage.")
        return response.text
    else:
        print(f"Failed to fetch the webpage. Status code: {response.status_code}")
        return None

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
        # Remove all classes, ids, and keep only the text information
        tag.attrs = {k: v for k, v in tag.attrs.items() if k not in ['class', 'id']}

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

# Main function to execute the full process
def analyze_website_accessibility(url):
    # Step 1: Fetch the website's HTML content
    html_content = fetch_website_html(url)
    if html_content is None:
        return

    # Step 2: Generate the two outputs (visual and impaired)
    visual_output, impaired_output = generate_accessible_html_outputs(html_content)

    # Step 3: Save the outputs to HTML files
    visual_output_path = 'output/visual_real_website_output.html'
    impaired_output_path = 'output/impaired_real_website_output.html'

    os.makedirs('output', exist_ok=True)  # Create the output directory if it doesn't exist

    with open(visual_output_path, 'w') as file:
        file.write(visual_output)

    with open(impaired_output_path, 'w') as file:
        file.write(impaired_output)

    print(f"Outputs saved:\n- Visual: {visual_output_path}\n- Impaired: {impaired_output_path}")

# Example usage
# website_url = 'https://gist.github.com/'
website_url = 'https://docs.stripe.com/'
analyze_website_accessibility(website_url)
