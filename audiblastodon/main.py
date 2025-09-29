import argparse
import os
import csv
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv
from audiblastodon.scraper import scrape_free_books, scrape_plus_books
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
        writer = csv.DictWriter(f, fieldnames=['title', 'author', 'link', 'source', 'scraped_at', 'posted_at'])
        writer.writeheader()
        writer.writerows(books)

def append_book(file_path, book):
    """Append a single book to the CSV file."""
    file_exists = os.path.exists(file_path)
    with open(file_path, 'a') as f:
        writer = csv.DictWriter(f, fieldnames=['title', 'author', 'link', 'source', 'scraped_at', 'posted_at'])
        if not file_exists:
            writer.writeheader()
        writer.writerow(book)

def scrape(args):
    logging.info("Beginning scrape...")
    logging.info("Scraping Free Listens page...")
    free_books = scrape_free_books()
    for book in free_books:
        book['source'] = 'free'
    logging.info(f"Found {len(free_books)} books on the free listens page.")

    # Process and save free books immediately
    existing_books = get_books(args.books_file)
    existing_links = {book['link'] for book in existing_books}

    new_free_count = 0
    for book in free_books:
        if book['url'] not in existing_links:
            book_entry = {
                'title': book['title'],
                'author': book['author'],
                'link': book['url'],
                'source': book['source'],
                'scraped_at': datetime.now(timezone.utc).isoformat(),
                'posted_at': ''
            }

            if args.dry_run:
                logging.info(f"[DRY RUN] New free book: {book_entry['title']}")
            else:
                append_book(args.books_file, book_entry)
                logging.info(f"Added free book: {book_entry['title']}")
                existing_links.add(book['url'])

            new_free_count += 1

    if new_free_count > 0:
        logging.info(f"Found {new_free_count} new free books.")

    logging.info("Scraping Plus Catalog page...")
    plus_books = scrape_plus_books(save_page=args.savepage)
    for book in plus_books:
        book['source'] = 'plus'
    logging.info(f"Found {len(plus_books)} books on the plus catalog page.")

    # Process and save plus books immediately
    new_plus_count = 0
    for book in plus_books:
        if book['url'] not in existing_links:
            book_entry = {
                'title': book['title'],
                'author': book['author'],
                'link': book['url'],
                'source': book['source'],
                'scraped_at': datetime.now(timezone.utc).isoformat(),
                'posted_at': ''
            }

            if args.dry_run:
                logging.info(f"[DRY RUN] New plus book: {book_entry['title']}")
            else:
                append_book(args.books_file, book_entry)
                logging.info(f"Added plus book: {book_entry['title']}")
                existing_links.add(book['url'])

            new_plus_count += 1

    if new_plus_count > 0:
        logging.info(f"Found {new_plus_count} new plus books.")

    total_new = new_free_count + new_plus_count
    logging.info(f"Total new books found: {total_new}")

def post(args):
    logging.info("Posting new books...")
    if not os.path.exists(args.books_file):
        raise FileNotFoundError(f"Books file not found: {args.books_file}. Run with `scrape` to create it.")

    books = get_books(args.books_file)
    unposted_books = [book for book in books if not book['posted_at']]
    logging.info(f"Found {len(unposted_books)} unposted books.")
    if not (args.mastodon_instance and args.mastodon_token):
        logging.info("No Mastodon creds supplied.")
    if not args.discord_webhook:
        logging.info("No Discord creds supplied.")
    
    for book in unposted_books:
        if book.get('source') == 'plus':
            message = f"New Audible Plus release: {book['title']}\nby {book['author']}\n{book['link']}"
        else:
            message = f"New free Audible book: {book['title']}\nby {book['author']}\n{book['link']}"

        if args.dry_run:
            logging.info(f"[DRY RUN] {message}")
        else:

            if args.mastodon_instance and args.mastodon_token:
                post_to_mastodon(args.mastodon_instance, args.mastodon_token, message)
            if args.discord_webhook:
                post_to_discord(args.discord_webhook, message)
    
            # Update posted_at timestamp immediately
            book['posted_at'] = datetime.now(timezone.utc).isoformat()

            # Rewrite entire CSV with updated book
            all_books = get_books(args.books_file)
            for b in all_books:
                if b['link'] == book['link']:
                    b['posted_at'] = book['posted_at']
                    break
            write_books(args.books_file, all_books)
            logging.info(f"Updated posted_at for: {book['title']}")

def cli():
    parser = argparse.ArgumentParser(description="Find new Free On Audible books and post them to Mastodon and/or Discord.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Scrape command
    scrape_parser = subparsers.add_parser("scrape", help="Scrape for new books.")
    scrape_parser.add_argument("--dry-run", action="store_true", help="Dry run - print to log instead of writing to file.")
    scrape_parser.add_argument("--books-file", default="books.csv", help="The file to store the book data in.")
    scrape_parser.add_argument("--savepage", action="store_true", help="Save page HTML when scraping Plus catalog (for debugging).")
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