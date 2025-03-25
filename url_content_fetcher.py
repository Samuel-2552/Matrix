import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import sqlite3

def is_client_side_rendered(html_content):
    """Determine if a webpage is client-side rendered by checking HTML content."""
    url=normalize_url(url)
    if html_content != selenium_content:
        update_or_insert_url(url, True)  # Client-side rendered
        return True  # Client-side rendered
    else:
        update_or_insert_url(url, False) # Not client-side rendered
        return False  # Not client-side rendered

def fetch_content(url, retries=3):
    """Fetch webpage content, handle client-side rendering, and return detailed errors if needed."""
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
            html_content = response.text
            
            return {"status": "success", "content": html_content}
        
        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:
                time.sleep(2)  # Wait before retrying
                continue
            return {"status": "error", "message": str(e)}

def fetch_with_selenium(url, retries=3):
    """Use Selenium to fetch the full rendered content of a URL."""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    for attempt in range(retries):
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.set_page_load_timeout(15)
            driver.get(url)
            page_source = driver.page_source
            driver.quit()
            return {"status": "success", "content": page_source}
        
        except (WebDriverException, TimeoutException) as e:
            if attempt < retries - 1:
                time.sleep(2)  # Wait before retrying
                continue
            return {"status": "error", "message": str(e)}
    
# Example usage
url = "https://app.securin.io"
result = fetch_content(url)
print(result)
