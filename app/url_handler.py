# get_job.py
import requests
from bs4 import BeautifulSoup

def get_job(url: str) -> str:
    """Extract job description from LinkedIn job postings"""
    try:
        # Set headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # Fetch webpage
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the job description container - multiple selector options for robustness
        container = soup.find('article', class_='jobs-description__container') or \
                    soup.find('div', class_='jobs-description__content--condensed') or \
                    soup.body

        # Extract the main job content using observed LinkedIn structure
        content_div = container.find('div', class_='jobs-description-content__text--stretch')
        
        if not content_div:
            raise ValueError("Job description section not found")

        # Clean up the text
        text = content_div.get_text(separator='\n', strip=True)
        
        # Remove empty lines and excessive newlines
        cleaned_text = '\n'.join([line.strip() for line in text.split('\n') if line.strip()])

        return cleaned_text

    except Exception as e:
        raise RuntimeError(f"Failed to process LinkedIn job post: {str(e)}")
