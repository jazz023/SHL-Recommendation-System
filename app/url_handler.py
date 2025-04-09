import re
import requests
from bs4 import BeautifulSoup

# URL validation functions
def is_url(input_str):
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/?=\w&%-]*'
    return re.search(url_pattern, input_str) is not None

def extract_url(input_str):
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/?=\w&%-]*'
    match = re.search(url_pattern, input_str)
    return match.group(0) if match else None


# Job description extraction function
def get_job(url):
    try:
        # Set headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # Fetch webpage
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Create BeautifulSoup object
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the job description container
        description_section = soup.find('div', {'class': 'description__text description__text--rich'})
            
        # Clean and format the text
        cleaned_lines = [line.strip() for line in description_section.get_text(separator='\n').split('\n') if line.strip()]
        
        return '\n'.join(cleaned_lines)


    except Exception as e:
        raise RuntimeError(f"Failed to process LinkedIn job post: {str(e)}")