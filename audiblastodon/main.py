import argparse
import os
import csv
from datetime import datetime, timezone
import requests
from dotenv import load_dotenv
from audiblastodon.scraper import scrape_free_books
from audiblastodon.mastodon_poster import post_to_mastodon
from audiblastodon.discord_poster import post_to_discord

load_dotenv()

def get_books(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        return list(reader)

def write_books(file_path, books):
    with open(file_path, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=['title', 'author', 'link', 'scraped_at', 'posted_at'])
        writer.writeheader()
        writer.writerows(books)

def scrape(file_path, dry_run=False):
    print("Scraping for books...")
    html_content = requests.get("https://www.audible.com/ep/FreeListens").text
    scraped_books = scrape_free_books(html_content)
    print(f"Found {len(scraped_books)} books on the free listens page.")

    if dry_run:
        for book in scraped_books:
            print(f"[DRY RUN] Found book: {book['title']}")
        return

    existing_books = get_books(file_path)
    existing_links = {book['link'] for book in existing_books}

    new_books = []
    for book in scraped_books:
        if book['url'] not in existing_links:
            new_books.append({
                'title': book['title'],
                'author': book['author'],
                'link': book['url'],
                'scraped_at': datetime.now(timezone.utc).isoformat(),
                'posted_at': ''
            })
    
    print(f"Found {len(new_books)} new books.")
    all_books = existing_books + new_books
    write_books(file_path, all_books)

def post(file_path, mastodon_instance, mastodon_token, discord_webhook, dry_run=False):
    print("Posting new books...")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Books file not found: {file_path}. Run with --scrape to create it.")

    books = get_books(file_path)
    unposted_books = [book for book in books if not book['posted_at']]
    print(f"Found {len(unposted_books)} unposted books.")

    for book in unposted_books:
        message = f"New free Audible book: {book['title']}\nby {book['author']}\n{book['link']}"
        if dry_run:
            print(f"[DRY RUN] {message}")
        else:
            print(f"Posting new book: {book['title']}")
            if mastodon_instance and mastodon_token:
                post_to_mastodon(mastodon_instance, mastodon_token, message)
            if discord_webhook:
                post_to_discord(discord_webhook, message)
            book['posted_at'] = datetime.now(timezone.utc).isoformat()

    if not dry_run:
        write_books(file_path, books)

def cli():
    parser = argparse.ArgumentParser(description="Find new free Audible books and post them to Mastodon and/or Discord.")
    parser.add_argument("--scrape", action="store_true", help="Scrape for new books.")
    parser.add_argument("--post", action="store_true", help="Post new books.")
    parser.add_argument("--dry-run", action="store_true", help="Dry run - print to log instead of posting or writing to file.")
    parser.add_argument("--books-file", default="books.csv", help="The file to store the book data in.")
    parser.add_argument("--mastodon-instance", default=os.environ.get("MASTODON_INSTANCE"), help="The URL of your Mastodon instance.")
    parser.add_argument("--mastodon-token", default=os.environ.get("MASTODON_TOKEN"), help="Your Mastodon access token.")
    parser.add_argument("--discord-webhook", default=os.environ.get("DISCORD_WEBHOOK"), help="Your Discord webhook URL.")

    args = parser.parse_args()

    if not args.scrape and not args.post:
        parser.print_help()
        return

    if args.scrape:
        scrape(args.books_file, dry_run=args.dry_run)
    
    if args.post:
        post(args.books_file, args.mastodon_instance, args.mastodon_token, args.discord_webhook, dry_run=args.dry_run)

if __name__ == "__main__":
    cli()