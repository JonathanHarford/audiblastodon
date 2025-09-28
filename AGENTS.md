# Project Overview

This project is a Python-based bot that scrapes Audible's "Free Listens" page to find new free audiobooks and automatically posts them to a Mastodon account and/or a Discord channel.

## Key Technologies

*   **Python:** The core language for the bot's logic.
*   **Libraries:**
    *   `requests`: For making HTTP requests to Audible, Mastodon, and Discord.
    *   `beautifulsoup4`: For parsing the HTML content of the Audible page.
    *   `python-dotenv`: For managing environment variables.
    *   `pytest`: For running tests.
    *   `playwright`: For browser automation to scrape dynamic content.

## Architecture

The bot is structured into several modules:

*   `main.py`: The main entry point of the application. It handles command-line arguments, orchestrates the scraping and posting process, and manages the state of already posted books.
*   `scraper.py`: Contains the logic for scraping the Audible "Free Listens" page and the "Plus Catalog" to extract book titles and URLs.
*   `mastodon_poster.py`: Handles posting messages to a Mastodon instance.
*   `discord_poster.py`: Handles posting messages to a Discord webhook.
*   `test_*.py`: Unit tests for the different modules.

# Building and Running

This project uses `uv` for package management.

1.  **Install `uv`**

    Follow the official instructions to install `uv`: https://github.com/astral-sh/uv

2.  **Create a virtual environment**

    ```bash
    uv venv
    ```

3.  **Install dependencies**

    ```bash
    uv pip install -e .
    ```

4.  **Install Playwright browsers**
    ```bash
    uv run playwright install
    ```

5.  **Configuration**

    You can configure the bot using a `.env` file. Create a `.env` file in the root of the project and add the following variables:

    ```
    MASTODON_INSTANCE=<your-mastodon-instance-url>
    MASTODON_TOKEN=<your-access-token>
    DISCORD_WEBHOOK=<your-discord-webhook-url>
    ```

    You can also pass these values as command-line arguments.

6.  **Running the bot**

    You can run the bot from the command line. You must provide credentials for at least one service (Mastodon or Discord), either through the `.env` file or as command-line arguments.

    ```bash
    uv run main scrape
    uv run main post
    ```

### Running Commands

To run commands within the project's virtual environment, use `uv run`. This is particularly useful for executing scripts or tools that are installed as project dependencies.

For example, to run the main application's `scrape` command:

```bash
uv run main scrape
```

To run the scraper with the `--dry-run` flag:

```bash
uv run main scrape --dry-run
```

# Development Conventions

*   **Testing:** The project uses `pytest` for testing. Tests are located in files named `test_*.py`. To run the tests, execute the following command:
    ```bash
    uv run pytest
    ```

*   **Code Style:** The code follows standard Python conventions (PEP 8).
*   **State Management:** The bot keeps track of posted books by storing their URLs in a CSV file (`books.csv` by default).