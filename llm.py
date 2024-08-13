import openai
from bs4 import BeautifulSoup

def generate_accessibility_html(visual_element_html, impaired_element_html):
    """
    Query the LLM to generate a fully accessible version of the impaired element.
    """
    prompt = f"""
    You are given two HTML elements. The first element is from a fully accessible webpage:
    
    Visual Element:
    {visual_element_html}
    
    The second element is from an impaired version of the same webpage:
    
    Impaired Element:
    {impaired_element_html}
    
    Generate the fully accessible version of the impaired element by applying necessary accessibility enhancements (such as aria-labels, alt attributes, etc.) based on the content of the visual element.

    Output only the final enhanced HTML element. Do not include any explanations or additional text.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert in web accessibility."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=200
    )
    enhanced_html = response.choices[0].message['content'].strip()
    return enhanced_html

def enhance_impaired_html(tags_to_check):
    # Load HTML files
    with open('output/visual_output.html', 'r', encoding='utf-8') as file:
        visual_html_doc = file.read()

    with open('output/impaired_output.html', 'r', encoding='utf-8') as file:
        impaired_html_doc = file.read()

    # Parse HTML documents with BeautifulSoup
    visual_soup = BeautifulSoup(visual_html_doc, 'html.parser')
    impaired_soup = BeautifulSoup(impaired_html_doc, 'html.parser')

    # Process each tag type
    for tag in tags_to_check:
        visual_elements = visual_soup.find_all(tag)
        impaired_elements = impaired_soup.find_all(tag)

        # Ensure we only process the number of elements that exist in both documents
        for idx in range(min(len(visual_elements), len(impaired_elements))):
            impaired_element = impaired_elements[idx]
            visual_element_html = str(visual_elements[idx])

            if not impaired_element.get_text(strip=True):  # Check if the content is missing
                impaired_element_html = str(impaired_element)

                # Generate the enhanced HTML for the impaired element
                enhanced_html = generate_accessibility_html(visual_element_html, impaired_element_html)

                # Replace the impaired element with the enhanced version
                impaired_element.replace_with(BeautifulSoup(enhanced_html, 'html.parser'))

    # Save the updated impaired HTML document
    output_file_path = 'output/updated_impaired_output.html'
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(str(impaired_soup))

# List of tags to check for accessibility enhancements
tags_to_check = ['h1', 'h2', 'h3', 'p', 'img', 'a']

# Process the HTML files
enhance_impaired_html(tags_to_check)
