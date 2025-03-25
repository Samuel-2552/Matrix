import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import sqlite3

# Function to create the database and table if it doesn't exist
def create_TechStack_db():
    conn = sqlite3.connect('TechStack.db')
    cursor = conn.cursor()

    # Create the table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tech_stack (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        base_url TEXT,
        csr BOOLEAN
    )
    ''')

    conn.commit()
    conn.close()

# Function to normalize URLs (remove trailing slashes, make lowercase, and discard anything after the first '/')
def normalize_url(url):
    # Remove trailing slashes and convert to lowercase for case-insensitive comparison
    normalized_url = url.rstrip('/').lower()

    # Discard everything after the first '/'
    if '/' in normalized_url:
        normalized_url = normalized_url.split('/')[0]

    return normalized_url

# Function to update the record or insert a new one if the URL doesn't exist
def update_or_insert_url(base_url, csr):
    conn = sqlite3.connect('TechStack.db')
    cursor = conn.cursor()

    # Normalize the URL
    normalized_url = normalize_url(base_url)

    # Check if the URL already exists in the database
    cursor.execute('SELECT id FROM tech_stack WHERE LOWER(base_url) = LOWER(?)', (normalized_url,))
    result = cursor.fetchone()

    if result:
        # If URL exists, update the CSR value
        cursor.execute('UPDATE tech_stack SET csr = ? WHERE id = ?', (csr, result[0]))
    else:
        # If URL doesn't exist, insert a new record
        cursor.execute('INSERT INTO tech_stack (base_url, csr) VALUES (?, ?)', (normalized_url, csr))

    conn.commit()
    conn.close()

# Function to retrieve data by URL
def retrieve_by_url(base_url):
    conn = sqlite3.connect('TechStack.db')
    cursor = conn.cursor()

    # Normalize the URL
    normalized_url = normalize_url(base_url)

    # Retrieve the data for the URL
    cursor.execute('SELECT id, base_url, csr FROM tech_stack WHERE LOWER(base_url) = LOWER(?)', (normalized_url,))
    result = cursor.fetchone()

    conn.close()

    if result:
        return {
            "id": result[0],
            "base_url": result[1],
            "csr": result[2]
        }
    else:
        return None

def is_client_side_rendered(url, html_content, selenium_content):
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
