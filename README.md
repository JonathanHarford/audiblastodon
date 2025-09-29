# Audiblastodon

This bot finds new audiobooks on Audible's "Free Listens" and "Audible Plus" (i.e. free with subscription) pages and posts them to a Mastodon account and/or a Discord channel.

## Installation

This project uses `uv` for package management.

1.  **Install `uv`**

    Follow the official instructions to install `uv`: https://github.com/astral-sh/uv

2.  **Create a virtual environment**

    ```bash
    uv venv
    ```

3.  **Install dependencies**

    ```bash
    uv sync
    ```

4.  **Install in editable mode**

    ```bash
    uv pip install -e .
    ```

5.  **Install Playwright browsers**

    ```bash
    uv run playwright install
    ```
    
## Configuration

You can configure the bot in two ways:

1.  **Environment Variables (recommended)**

    Create a `.env` file in the root of the project and add the following variables:

    ```
    MASTODON_INSTANCE=<your-mastodon-instance-url>
    MASTODON_TOKEN=<your-access-token>
    DISCORD_WEBHOOK=<your-discord-webhook-url>
    ```

    A `.env.example` file is provided as a template.

2.  **Command-line Arguments**

    You can also pass credentials as command-line arguments when running the bot. See the [Usage](#usage) section for examples.

You need to configure at least one of the following: Mastodon or Discord.

### Mastodon

1.  **Get a Mastodon Access Token**

    You need to create a Mastodon application to get an access token.
    
    - Go to your Mastodon instance's settings: `https://<your-instance>/settings/applications`
    - Click "New Application".
    - Give your application a name (e.g., "Audiblastodon").
    - Make sure the `write:statuses` scope is checked.
    - Click "Submit".
    - You will see your access token on the next page. Copy it.

### Discord

1.  **Get a Discord Webhook URL**

    - In your Discord server, go to Server Settings > Integrations > Webhooks.
    - Click "New Webhook".
    - Give the webhook a name (e.g., "Audiblastodon").
    - Choose the channel you want the bot to post in.
    - Click "Copy Webhook URL".

## Usage

The bot has two main commands: `scrape` and `post`.

*   `scrape`: Scrapes Audible for new books and adds them to `books.csv`.
*   `post`: Posts any unposted books from `books.csv`.

Each command has a `--dry-run` option that will print the output to the console instead of performing the action.

### Examples

*   **To scrape for new books:**
    ```bash
    uv run main scrape
    ```

*   **To post new books:**
    ```bash
    uv run main post
    ```

*   **To do a dry run of the scrape:**
    ```bash
    uv run main scrape --dry-run
    ```

*   **To do a dry run of the post:**
    ```bash
    uv run main post --dry-run
    ```

## Running on a Schedule

To run this bot automatically, you can set up cron jobs to execute the commands periodically. It is recommended to run the `scrape` command more frequently than the `post` command.

For example, to scrape every hour and post every day at 9:00 AM:

```
0 * * * * cd /path/to/audiblastodon && uv run main scrape
0 9 * * * cd /path/to/audiblastodon && uv run main post
```
