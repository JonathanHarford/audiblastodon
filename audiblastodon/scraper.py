from bs4 import BeautifulSoup
import requests
from playwright.sync_api import sync_playwright, TimeoutError

def _parse_books_from_html(html_content):
    """
    Parses the HTML content to find audiobooks.

    Args:
        html_content: The HTML content of the page.

    Returns:
        A list of dictionaries, where each dictionary represents a book
        and has "title" and "url" keys.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    books = []
    product_list = soup.find_all('adbl-product-grid-item')

    for item in product_list:
        title_element = item.find('adbl-metadata', attrs={'slot': 'title'})
        author_element = item.find('adbl-metadata', attrs={'slot': 'author'})
        if title_element:
            link = title_element.find('a')
            author_link = author_element.find('a') if author_element else None
            if link:
                title = link.text.strip()
                url = f"https://www.audible.com{link['href']}"
                author = author_link.text.strip() if author_link else ""
                books.append({'title': title, 'author': author, 'url': url})
            
    return books

def scrape_free_books():
    """
    Scrapes the Audible "Free Listens" page to find free audiobooks.
    """
    html_content = requests.get("https://www.audible.com/ep/FreeListens").text
    return _parse_books_from_html(html_content)

def scrape_plus_books():
    """
    Scrapes the Audible Plus catalog for free audiobooks.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto("https://www.audible.com/search")
            
            try:
                page.locator('#sp-cc-accept').click(timeout=5000)
            except TimeoutError:
                pass # No cookie banner

            page.get_by_role("button", name="Plus Catalog").click()
            page.wait_for_load_state("networkidle")
            html_content = page.content()
            return _parse_books_from_html(html_content)
        except Exception as e:
            page.screenshot(path="error.png")
            raise e
        finally:
            browser.close()