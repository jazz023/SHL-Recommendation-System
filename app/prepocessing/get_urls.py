import requests
from bs4 import BeautifulSoup
import csv

base_url = "https://www.shl.com"
all_products = []

# Function to scrape a single page
def scrape_page(url):
    print(f"Scraping {url}")
    try:
        # Get the HTML content
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all product rows
        rows = soup.select('tr[data-entity-id]')
        
        for row in rows:
            # Extract name and URL from the link
            link_element = row.select_one('td.custom_table-heading_title a')
            if link_element:
                name = link_element.text.strip()
                product_url = base_url + link_element['href']
                
                # Find the IRT column and check for the green circle
                # Look for the third column with custom__table-heading__general class
                irt_cells = row.select('td.custom__table-heading__general')
                has_irt = "No"
                if len(irt_cells) >= 2:  # Based on the image, IRT appears to be the 2nd general column
                    irt_cell = irt_cells[1]  # Index 1 is the second cell
                    irt_element = irt_cell.select_one('span.catalogue__circle.-yes')
                    has_irt = "Yes" if irt_element else "No"
                
                product = {
                    "name": name,
                    "url": product_url,
                    "irt": has_irt
                }
                if product not in all_products:
                    all_products.append(product)
        
        print(f"  Extracted {len(rows)} products")
        return 0
    except Exception as e:
        print(f"  Error scraping page: {e}")
        return 0
        
# Scrape Individual Test Solutions (type=1)
total_pages_type1 = 32
for page in range(total_pages_type1):
    start = page * 12
    url = f"https://www.shl.com/solutions/products/product-catalog/?start={start}&type=1"
    scrape_page(url)
   
# Save results to CSV
with open('shl_products.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['name', 'url', 'irt'])
    writer.writeheader()
    writer.writerows(all_products)

print(f"Scraping completed. Total products extracted: {len(all_products)}")
print(f"Results saved to shl_products.csv")
