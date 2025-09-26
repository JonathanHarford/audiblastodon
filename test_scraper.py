import pytest
from pathlib import Path
from audiblastodon.scraper import scrape_free_books

@pytest.fixture
def sample_html():
    """Reads the sample HTML file."""
    path = Path(__file__).parent / "sample_audible_page.html"
    return path.read_text()

def test_scrape_free_books(sample_html):
    """
    Tests that the scrape_free_books function correctly extracts
    book titles and URLs from the sample HTML.
    """
    expected = [
        {"title": "The Motherlode Audiobook", "author": "Clover Hope", "url": "https://www.audible.com/pd/The-Motherlode-Audiobook/B0CBQLZF4M"},
        {"title": "First Eat with Nakkiah Lui Audiobook", "author": "Nakkiah Lui", "url": "https://www.audible.com/pd/First-Eat-with-Nakkiah-Lui-Audiobook/B0C5XLBN64"},
        {"title": "A Tale of Two Cities", "author": "Charles Dickens", "url": "https://www.audible.com/pd/A-Tale-of-Two-Cities-Audiobook/B0773Z4GB6"},
    ]
    
    actual = scrape_free_books(sample_html)
    
    assert actual == expected
