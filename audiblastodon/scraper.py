from bs4 import BeautifulSoup
import requests
import logging
from playwright.sync_api import sync_playwright, TimeoutError

def _save_debug_files(page):
    """Save screenshot and HTML for debugging purposes."""
    try:
        page.screenshot(path="error.png")
        logging.error("Screenshot saved to error.png")
    except Exception as e:
        logging.error(f"Could not save screenshot: {e}")

    try:
        with open("audible_plus_page.html", "w", encoding="utf-8") as f:
            f.write(page.content())
        logging.error("Page HTML saved to audible_plus_page.html")
    except Exception as e:
        logging.error(f"Could not save page HTML: {e}")

    # Log available elements with role="button"
    try:
        logging.error("Available elements with role='button':")
        button_elements = page.locator('[role="button"]').all()
        for i, element in enumerate(button_elements[:10]):  # Log first 10
            try:
                text = element.text_content() or element.get_attribute("aria-label") or "No text"
                logging.error(f"  Element {i+1}: '{text.strip()}'")
            except:
                logging.error(f"  Element {i+1}: Could not read text")
    except Exception as e:
        logging.error(f"Could not enumerate button elements: {e}")

def _parse_free_books_from_html(html_content):
    """
    Parses the HTML content from Free Listens page to find audiobooks.

    Args:
        html_content: The HTML content of the page.

    Returns:
        A list of dictionaries, where each dictionary represents a book
        and has "title", "author", and "url" keys.
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
                # Strip query parameters from URL to avoid duplicates
                href = link['href'].split('?')[0]
                url = f"https://www.audible.com{href}"
                author = author_link.text.strip() if author_link else ""
                books.append({'title': title, 'author': author, 'url': url})

    return books

def _parse_plus_books_from_html(html_content):
    """
    Parses the HTML content from Plus Catalog search page to find audiobooks.

    Args:
        html_content: The HTML content of the page.

    Returns:
        A list of dictionaries, where each dictionary represents a book
        and has "title", "author", and "url" keys.
    """
    logging.info("Starting to parse Plus Catalog HTML content")
    soup = BeautifulSoup(html_content, 'html.parser')
    books = []
    product_items = soup.find_all('li', class_='productListItem')
    logging.info(f"Found {len(product_items)} product items in HTML")

    for idx, item in enumerate(product_items):
        # Find the title in the h3 heading
        title_heading = item.find('h3', class_='bc-heading')
        if not title_heading:
            logging.info(f"Item {idx + 1}: No title heading found, skipping")
            continue

        title_link = title_heading.find('a', href=True)
        if not title_link:
            logging.info(f"Item {idx + 1}: No title link found in heading, skipping")
            continue

        title = title_link.get_text(strip=True)
        # Strip query parameters from URL to avoid duplicates
        href = title_link['href'].split('?')[0]
        url = f"https://www.audible.com{href}"
        logging.info(f"Item {idx + 1}: Title: '{title}', URL: {href}")

        # Find author from the authorLabel list item
        author = ""
        author_label = item.find('li', class_='authorLabel')
        if author_label:
            author_link = author_label.find('a', class_='bc-link')
            if author_link:
                author = author_link.get_text(strip=True)

        logging.info(f"Item {idx + 1}: Author: '{author}'")

        if title and url:
            books.append({'title': title, 'author': author, 'url': url})
        else:
            logging.info(f"Item {idx + 1}: Missing title or URL, skipping")

    logging.info(f"Finished parsing, found {len(books)} valid books")
    return books

def scrape_free_books():
    """
    Scrapes the Audible "Free Listens" page to find free audiobooks.
    """
    html_content = requests.get("https://www.audible.com/ep/FreeListens").text
    return _parse_free_books_from_html(html_content)

def scrape_plus_books(save_page=False):
    """
    Scrapes the Audible Plus catalog for free audiobooks.

    Args:
        save_page: If True, save page HTML on successful scrape for debugging.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            logging.info("Navigating to Audible Plus member benefit page...")
            page.goto("https://www.audible.com/ep/audible-plus-member-benefit", timeout=60000, wait_until="domcontentloaded")

            logging.info("Checking for cookie banner...")
            try:
                page.locator('#sp-cc-accept').click(timeout=3000)
                logging.info("Accepted cookie banner")
            except TimeoutError:
                logging.info("No cookie banner found")

            logging.info("Looking for 'Explore' button...")
            try:
                # Try both button role and link with button role
                explore_button = page.get_by_role('button', name="Explore")
                if not explore_button.is_visible():
                    logging.error("Explore button is not visible on page")
                    _save_debug_files(page)
                    raise RuntimeError("Explore button not visible")

                logging.info("Clicking 'Explore' button...")
                explore_button.click(timeout=5000)

                logging.info("Waiting for search page to load...")
                page.wait_for_load_state("networkidle", timeout=10000)

                # Set filters and sort order
                logging.info("Setting filters and sort order...")
                try:
                    # Select publication date filter - use force click to bypass overlay
                    page.get_by_role('link', { name: 'Last 30 Days Last 30 Days' }).click()
  
                    # Set sort order to publication date (newest first)
                    page.getByLabel('Sort by').selectOption('pubdate-desc-rank')
                    logging.info("Selected 'pubdate-desc-rank' sort option")

                    # Wait for page to reload with new filters and sort order
                    page.wait_for_load_state("networkidle", timeout=10000)
                except Exception as e:
                    logging.warning(f"Could not set filters/sort order: {e}")

                # Wait for actual product content to load
                logging.info("Waiting for book content to appear...")
                try:
                    # Wait for Plus catalog product list items
                    page.wait_for_selector('.productListItem', timeout=10000)
                    logging.info("Found product elements on page")
                except:
                    logging.warning("No product elements found, page might still be loading or structure changed")

                logging.info("Extracting page content...")
                html_content = page.content()
                books = _parse_plus_books_from_html(html_content)
                logging.info(f"Successfully parsed {len(books)} books from Plus Catalog")

                if save_page:
                    try:
                        with open("audible_plus_page.html", "w", encoding="utf-8") as f:
                            f.write(html_content)
                        logging.info("Page HTML saved to audible_plus_page.html")
                    except Exception as e:
                        logging.error(f"Could not save page HTML: {e}")

                return books

            except TimeoutError as e:
                logging.error(f"Timeout waiting for Explore button: {e}")
                _save_debug_files(page)
                raise RuntimeError("Could not find or click Explore button") from e

        except Exception as e:
            logging.error(f"Error scraping Plus Catalog: {e}")
            _save_debug_files(page)
            raise e
        finally:
            browser.close()