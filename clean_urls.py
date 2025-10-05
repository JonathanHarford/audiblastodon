#!/usr/bin/env python3
"""
Script to clean up book URLs in the CSV file by:
1. Stripping query parameters from URLs
2. Removing duplicate entries (keeping the earliest scraped entry)
"""
import csv
import sys
from datetime import datetime

def clean_url(url):
    """Strip query parameters from URL."""
    return url.split('?')[0]

def clean_books_csv(input_file, output_file=None):
    """Clean URLs and remove duplicates from books CSV."""
    if output_file is None:
        output_file = input_file

    # Read all books
    with open(input_file, 'r') as f:
        reader = csv.DictReader(f)
        books = list(reader)

    print(f"Total books before cleaning: {len(books)}")

    # Clean URLs and track duplicates
    seen_urls = {}
    cleaned_books = []
    duplicates_removed = 0
    urls_cleaned = 0

    for book in books:
        original_url = book['link']
        clean_url_value = clean_url(original_url)

        if original_url != clean_url_value:
            urls_cleaned += 1
            book['link'] = clean_url_value

        # Check for duplicates - keep earliest scraped
        if clean_url_value in seen_urls:
            duplicates_removed += 1
            existing = seen_urls[clean_url_value]
            # Keep the one with earlier scraped_at timestamp
            if book['scraped_at'] < existing['scraped_at']:
                # Replace with earlier one
                cleaned_books.remove(existing)
                cleaned_books.append(book)
                seen_urls[clean_url_value] = book
            # else: skip this one, keep existing
        else:
            seen_urls[clean_url_value] = book
            cleaned_books.append(book)

    # Write cleaned books back
    with open(output_file, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=['title', 'author', 'link', 'source', 'scraped_at', 'posted_at'])
        writer.writeheader()
        writer.writerows(cleaned_books)

    print(f"URLs cleaned: {urls_cleaned}")
    print(f"Duplicates removed: {duplicates_removed}")
    print(f"Total books after cleaning: {len(cleaned_books)}")
    print(f"Saved to: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python clean_urls.py <books.csv> [output.csv]")
        print("If output.csv not specified, will overwrite input file")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    clean_books_csv(input_file, output_file)
