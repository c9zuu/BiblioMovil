import requests
from bs4 import BeautifulSoup
import trafilatura
import pandas as pd
import time
import re

def scrape_website(url):
    """
    Scrape the full content of a website using Trafilatura.
    
    Parameters:
    ----------
    url : str
        URL of the website to scrape
        
    Returns:
    -------
    str
        The main text content of the website
    """
    try:
        # Send a request to the website
        downloaded = trafilatura.fetch_url(url)
        if downloaded is None:
            # Fallback to requests if trafilatura fails
            response = requests.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            response.raise_for_status()
            text = trafilatura.extract(response.text)
        else:
            text = trafilatura.extract(downloaded)
            
        if text is None:
            # If trafilatura extraction fails, use BeautifulSoup as fallback
            response = requests.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()
                
            # Get text
            text = soup.get_text(separator='\n')
            
            # Clean up text: remove multiple newlines and whitespace
            text = re.sub(r'\n+', '\n', text)
            text = re.sub(r' +', ' ', text)
            text = text.strip()
            
        return text
    except Exception as e:
        raise Exception(f"Failed to scrape website: {str(e)}")

def extract_data_with_selectors(url, selectors, attribute_name=None, pagination_config=None):
    """
    Extract data from a website using CSS selectors.
    
    Parameters:
    ----------
    url : str
        URL of the website to scrape
    selectors : dict
        Dictionary of field names and corresponding CSS selectors
    attribute_name : str, optional
        Name of the attribute to extract instead of text (e.g., 'href', 'src')
    pagination_config : dict, optional
        Configuration for pagination with keys:
        - enabled: bool
        - selector: str (CSS selector for next page)
        - max_pages: int (maximum number of pages to scrape)
        
    Returns:
    -------
    list
        List of dictionaries containing the extracted data
    """
    try:
        results = []
        current_url = url
        page_count = 0
        max_pages = 1  # Default to 1 page if pagination not enabled
        
        if pagination_config and pagination_config.get('enabled', False):
            max_pages = pagination_config.get('max_pages', 1)
        
        while page_count < max_pages:
            # Send a request to the current page
            response = requests.get(current_url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            response.raise_for_status()
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check if we're extracting multiple items (list) or single items
            # If any selector returns multiple elements, we'll treat it as a list extraction
            is_list_extraction = False
            sample_selector = list(selectors.values())[0]
            if len(soup.select(sample_selector)) > 1:
                is_list_extraction = True
            
            if is_list_extraction:
                # Get the maximum number of items for any selector
                max_items = max([len(soup.select(selector)) for selector in selectors.values()])
                
                # Extract data for each item
                for i in range(max_items):
                    item_data = {}
                    for field_name, selector in selectors.items():
                        elements = soup.select(selector)
                        if i < len(elements):
                            if attribute_name:
                                # Extract attribute value
                                item_data[field_name] = elements[i].get(attribute_name, '')
                            else:
                                # Extract text
                                item_data[field_name] = elements[i].get_text(strip=True)
                        else:
                            item_data[field_name] = ''
                    
                    # Only add non-empty items
                    if any(item_data.values()):
                        results.append(item_data)
            else:
                # Single item extraction
                item_data = {}
                for field_name, selector in selectors.items():
                    elements = soup.select(selector)
                    if elements:
                        if attribute_name:
                            # Extract attribute value
                            item_data[field_name] = elements[0].get(attribute_name, '')
                        else:
                            # Extract text
                            item_data[field_name] = elements[0].get_text(strip=True)
                    else:
                        item_data[field_name] = ''
                
                # Only add non-empty items
                if any(item_data.values()):
                    results.append(item_data)
            
            page_count += 1
            
            # Check if pagination is enabled and there's a next page
            if pagination_config and pagination_config.get('enabled', False):
                next_button = soup.select_one(pagination_config.get('selector', ''))
                if next_button and next_button.get('href'):
                    # Get the next page URL
                    next_url = next_button['href']
                    
                    # Handle relative URLs
                    if not next_url.startswith('http'):
                        if next_url.startswith('/'):
                            # Absolute path relative to domain
                            base_url = re.match(r'(https?://[^/]+)', current_url).group(1)
                            next_url = base_url + next_url
                        else:
                            # Relative path to current URL
                            current_url_base = current_url.rsplit('/', 1)[0]
                            next_url = f"{current_url_base}/{next_url}"
                    
                    current_url = next_url
                    
                    # Add a small delay to avoid overloading the server
                    time.sleep(1)
                else:
                    # No next page found, break the loop
                    break
            else:
                # Pagination not enabled, break after first page
                break
        
        return results
    except Exception as e:
        raise Exception(f"Failed to extract data with selectors: {str(e)}")
