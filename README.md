# Audible Freebie Bot

This bot finds new free audiobooks on Audible's "Free Listens" page and posts them to a Mastodon account and/or a Discord channel.

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
    - Give your application a name (e.g., "Audible Freebie Bot").
    - Make sure the `write:statuses` scope is checked.
    - Click "Submit".
    - You will see your access token on the next page. Copy it.

### Discord

1.  **Get a Discord Webhook URL**

    - In your Discord server, go to Server Settings > Integrations > Webhooks.
    - Click "New Webhook".
    - Give the webhook a name (e.g., "Audible Freebie Bot").
    - Choose the channel you want the bot to post in.
    - Click "Copy Webhook URL".

## Usage

You can run the bot from the command line. If you have configured the bot using a `.env` file, you can simply run:

```bash
uv run main
```

If you prefer to use command-line arguments, you can do so as follows:

### Post to Mastodon
```bash
uv run main -- \
    --mastodon-instance <your-mastodon-instance-url> \
    --mastodon-token <your-access-token>
```

### Post to Discord
```bash
uv run main -- \
    --discord-webhook <your-discord-webhook-url>
```

### Post to Both
```bash
uv run main -- \
    --mastodon-instance <your-mastodon-instance-url> \
    --mastodon-token <your-access-token> \
    --discord-webhook <your-discord-webhook-url>
```

The bot will create a file named `posted_books.txt` in the current directory to keep track of the books it has already posted. You can change this with the `--posted-books-file` argument.

### Running on a Schedule

To run this bot automatically, you can set up a cron job or a similar scheduling mechanism to execute the command periodically (e.g., once a day).
