import argparse
import os
import csv
import logging
from datetime import datetime, timezone
import requests
from dotenv import load_dotenv
from audiblastodon.scraper import scrape_free_books
from audiblastodon.mastodon_poster import post_to_mastodon
from audiblastodon.discord_poster import post_to_discord

load_dotenv()

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

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

def scrape(args):
    logging.info("Scraping for books...")
    html_content = requests.get("https://www.audible.com/ep/FreeListens").text
    scraped_books = scrape_free_books(html_content)
    logging.info(f"Found {len(scraped_books)} books on the free listens page.")

    existing_books = get_books(args.books_file)
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

    logging.info(f"Found {len(new_books)} new books.")

    if args.dry_run:
        for book in new_books:
            logging.info(f"[DRY RUN] Found new book: {book['title']}")
        return

    all_books = existing_books + new_books
    write_books(args.books_file, all_books)

def post(args):
    logging.info("Posting new books...")
    if not os.path.exists(args.books_file):
        raise FileNotFoundError(f"Books file not found: {args.books_file}. Run with `scrape` to create it.")

    books = get_books(args.books_file)
    unposted_books = [book for book in books if not book['posted_at']]
    logging.info(f"Found {len(unposted_books)} unposted books.")

    for book in unposted_books:
        message = f"New free Audible book: {book['title']}\nby {book['author']}\n{book['link']}"
        if args.dry_run:
            logging.info(f"[DRY RUN] {message}")
        else:
            logging.info(f"Posting new book: {book['title']}")
            if args.mastodon_instance and args.mastodon_token:
                post_to_mastodon(args.mastodon_instance, args.mastodon_token, message)
            if args.discord_webhook:
                post_to_discord(args.discord_webhook, message)
            book['posted_at'] = datetime.now(timezone.utc).isoformat()

    if not args.dry_run:
        write_books(args.books_file, books)

def cli():
    parser = argparse.ArgumentParser(description="Find new free Audible books and post them to Mastodon and/or Discord.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Scrape command
    scrape_parser = subparsers.add_parser("scrape", help="Scrape for new books.")
    scrape_parser.add_argument("--dry-run", action="store_true", help="Dry run - print to log instead of writing to file.")
    scrape_parser.add_argument("--books-file", default="books.csv", help="The file to store the book data in.")
    scrape_parser.set_defaults(func=scrape)

    # Post command
    post_parser = subparsers.add_parser("post", help="Post new books.")
    post_parser.add_argument("--dry-run", action="store_true", help="Dry run - print to log instead of posting.")
    post_parser.add_argument("--books-file", default="books.csv", help="The file to store the book data in.")
    post_parser.add_argument("--mastodon-instance", default=os.environ.get("MASTODON_INSTANCE"), help="The URL of your Mastodon instance.")
    post_parser.add_argument("--mastodon-token", default=os.environ.get("MASTODON_TOKEN"), help="Your Mastodon access token.")
    post_parser.add_argument("--discord-webhook", default=os.environ.get("DISCORD_WEBHOOK"), help="Your Discord webhook URL.")
    post_parser.set_defaults(func=post)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    cli()