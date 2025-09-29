#!/usr/bin/env python3

# uv run test_parse.py

import logging
from audiblastodon.scraper import _parse_plus_books_from_html

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

with open('audible_plus_page.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

books = _parse_plus_books_from_html(html_content)

print(f"\nTotal books found: {len(books)}")
for book in books:
    print(f"  - {book['title']} by {book['author']}")
    print(f"    {book['url']}")