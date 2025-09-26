import pytest
import csv
from pathlib import Path
from audiblastodon.main import scrape, post

@pytest.fixture
def mock_scraper_requests(mocker):
    """Mocks the requests.get call to return a fixed HTML content."""
    return mocker.patch(
        'requests.get',
        return_value=mocker.Mock(
            text='''
            <adbl-product-grid-item>
                <adbl-metadata slot="title">
                    <a href="/pd/New-Book-Audiobook/B0C123456">New Book</a>
                </adbl-metadata>
                <adbl-metadata slot="author">
                    <a href="/author/New-Author/B0C123456">New Author</a>
                </adbl-metadata>
            </adbl-product-grid-item>
            <adbl-product-grid-item>
                <adbl-metadata slot="title">
                    <a href="/pd/Old-Book-Audiobook/B0Cabcdef">Old Book</a>
                </adbl-metadata>
                <adbl-metadata slot="author">
                    <a href="/author/Old-Author/B0Cabcdef">Old Author</a>
                </adbl-metadata>
            </adbl-product-grid-item>
            '''
        )
    )

@pytest.fixture
def books_file(tmp_path):
    """Creates a temporary file for books with one 'old' book."""
    file_path = tmp_path / "books.csv"
    with open(file_path, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=['title', 'author', 'link', 'scraped_at', 'posted_at'])
        writer.writeheader()
        writer.writerow({
            'title': 'Old Book',
            'author': 'Old Author',
            'link': 'https://www.audible.com/pd/Old-Book-Audiobook/B0Cabcdef',
            'scraped_at': '2025-01-01T00:00:00+00:00',
            'posted_at': '2025-01-01T00:00:00+00:00'
        })
    return file_path

def test_scrape_creates_file(mock_scraper_requests, tmp_path):
    file_path = tmp_path / "books.csv"
    scrape(file_path)
    assert file_path.exists()

def test_scrape_adds_new_book(mock_scraper_requests, books_file):
    scrape(books_file)
    with open(books_file, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 2
        assert rows[1]['title'] == 'New Book'

def test_scrape_dry_run(mock_scraper_requests, books_file, capsys):
    scrape(books_file, dry_run=True)
    captured = capsys.readouterr()
    assert "[DRY RUN] Found book: New Book" in captured.out

def test_post_posts_unposted_book(mocker, books_file):
    mock_post_mastodon = mocker.patch('audiblastodon.main.post_to_mastodon')
    mock_post_discord = mocker.patch('audiblastodon.main.post_to_discord')
    with open(books_file, 'a') as f:
        writer = csv.DictWriter(f, fieldnames=['title', 'author', 'link', 'scraped_at', 'posted_at'])
        writer.writerow({
            'title': 'Unposted Book',
            'author': 'Unposted Author',
            'link': 'https://www.audible.com/pd/Unposted-Book-Audiobook/B0Cfedcba',
            'scraped_at': '2025-01-01T00:00:00+00:00',
            'posted_at': ''
        })
    post(books_file, "https://mastodon.social", "token", "webhook")
    assert mock_post_mastodon.called
    assert mock_post_discord.called

def test_post_updates_posted_at(mocker, books_file):
    mocker.patch('audiblastodon.main.post_to_mastodon')
    mocker.patch('audiblastodon.main.post_to_discord')
    with open(books_file, 'a') as f:
        writer = csv.DictWriter(f, fieldnames=['title', 'author', 'link', 'scraped_at', 'posted_at'])
        writer.writerow({
            'title': 'Unposted Book',
            'author': 'Unposted Author',
            'link': 'https://www.audible.com/pd/Unposted-Book-Audiobook/B0Cfedcba',
            'scraped_at': '2025-01-01T00:00:00+00:00',
            'posted_at': ''
        })
    post(books_file, "https://mastodon.social", "token", "webhook")
    with open(books_file, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert rows[1]['posted_at'] != ''

def test_post_dry_run(mocker, books_file, capsys):
    mocker.patch('audiblastodon.main.post_to_mastodon')
    mocker.patch('audiblastodon.main.post_to_discord')
    with open(books_file, 'a') as f:
        writer = csv.DictWriter(f, fieldnames=['title', 'author', 'link', 'scraped_at', 'posted_at'])
        writer.writerow({
            'title': 'Unposted Book',
            'author': 'Unposted Author',
            'link': 'https://www.audible.com/pd/Unposted-Book-Audiobook/B0Cfedcba',
            'scraped_at': '2025-01-01T00:00:00+00:00',
            'posted_at': ''
        })
    post(books_file, "https://mastodon.social", "token", "webhook", dry_run=True)
    captured = capsys.readouterr()
    assert "[DRY RUN] New free Audible book: Unposted Book" in captured.out

def test_post_errors_if_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        post(tmp_path / "non_existent_file.csv", "https://mastodon.social", "token", "webhook")