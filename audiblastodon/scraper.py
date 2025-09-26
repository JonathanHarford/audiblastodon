from bs4 import BeautifulSoup

def scrape_free_books(html_content):
    """
    Scrapes the Audible "Free Listens" page to find free audiobooks.

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
