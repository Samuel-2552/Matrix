# main.py
import url_content_fetcher
import link_extraction
import screenshot

def main(urls, keywords):
    for url in urls:
        print(f"Processing: {url}")
        
        # Fetch content and determine if it requires Selenium
        content = url_content_fetcher.fetch_content(url)
        
        # Extract links
        internal_links, external_links = link_extraction.extract_links(content)
        
        # Search for keywords and take screenshots if needed
        keyword_matches = screenshot.find_keywords(content, keywords)
        if keyword_matches:
            keyword_matches=screenshot.capture(url, keyword_matches)
        
        print(f"Done processing: {url}\n")

if __name__ == "__main__":
    urls = ["https://example.com"]  # Replace with actual list of URLs
    keywords = ["login", "checkout", "payment"]  # Replace with actual keywords
    main(urls, keywords)
