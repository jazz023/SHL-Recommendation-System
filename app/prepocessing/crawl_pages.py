import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv

# Load the CSV data to get URLs and IRT information
df = pd.read_csv('shl_products.csv')

# Create output file
with open('shl_product_details.csv', 'w', newline='', encoding='utf-8') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(['Name', 'Description', 'URL', 'Remote Testing', 'Adaptive/IRT Support', 'Duration', 'Test Type'])
    
    # Process each URL in the CSV
    for index, row in df.iterrows():
        name = row['name']
        url = row['url']
        irt = row['irt']
        
        try:
            # Fetch the page
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract description
            description_elem = soup.select_one('.product-catalogue-training-calendar__row h4:contains("Description") + p')
            description = description_elem.text.strip() if description_elem else "N/A"
            
            # Extract duration
            duration_elem = soup.select_one('.product-catalogue-training-calendar__row h4:contains("Assessment length") + p')
            duration = duration_elem.text.strip() if duration_elem else "N/A"
            
            # Extract Remote Testing
            remote_test_elem = soup.select_one('.catalogue__circle.-yes')
            remote_testing = "Yes" if remote_test_elem else "No"
            
            # Extract Test Type (the letters)
            test_type_elem = soup.select('.product-catalogue__key')
            test_type = ''.join([elem.text.strip() for elem in test_type_elem]) if test_type_elem else "N/A"
            test_type = test_type[:-8]
            
            # Write to CSV
            writer.writerow([name, description, url, remote_testing, irt, duration, test_type])
            
            print(f"Processed: {name}")
            
        except Exception as e:
            print(f"Error processing {url}: {e}")
            writer.writerow([name, "Error", url, "Error", irt, "Error", "Error"])
