# TG-notetaker User Manual

## 1. Introduction
**TG-notetaker** is a powerful Telegram bot that automatically records group chat messages and uses AI to generate daily summaries. It helps you keep track of important discussions without reading every single message.

## 2. Installation & Setup

### Prerequisites
- Python 3.8+
- A Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- (Optional) OpenAI or Anthropic API Key for summaries

### Step-by-Step Installation

1.  **Clone the Repository**
    ```bash
    git clone <your-repo-url>
    cd TG-notetaker
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment**
    Copy the example configuration file:
    ```bash
    cp .env.example .env
    ```
    Edit `.env` with your credentials (see Configuration section).

4.  **Run the Bot**
    ```bash
    ./run.sh
    # OR
    python src/bot.py
    ```

### Docker Deployment
You can also run the bot using Docker:
```bash
docker-compose up -d
```

## 3. Configuration
Edit the `.env` file to configure the bot.

### Essential Settings
- `TELEGRAM_BOT_TOKEN`: Your Bot Token.
- `ADMIN_IDS`: Comma-separated list of user IDs who are admins (e.g., `123456789,987654321`).
- `ALLOWED_GROUPS`: (Optional) Comma-separated list of group IDs to record. If empty, all groups are recorded.

### AI Summary Settings
- `ENABLE_AI_SUMMARY`: Set to `true` to enable.
- `AI_PROVIDER`: `openai` or `anthropic`.
- `OPENAI_API_KEY`: Your API key.
- `SUMMARY_LANGUAGE`: `zh` (Chinese), `en` (English), etc.
- `SUMMARY_LENGTH`: `short`, `medium`, `long`.
- `AUTO_SUMMARY_TIME`: Time to run daily summary (e.g., `00:00`).

## 4. Usage Guide

### 4.1 Basic Commands
These commands are available in the chat input menu (`/`):

- `/start`: Show welcome message and help.
- `/help`: Display detailed usage instructions.
- `/myid`: Get your Telegram User ID (useful for configuration).

### 4.2 Admin Commands
Only users listed in `ADMIN_IDS` can use these:

- `/menu`: Open the interactive control panel (**Recommended**).
- `/stats`: View group activity statistics.
- `/status`: Check bot health and uptime.
- `/summary [date]`: Manually trigger a summary.
    - `/summary 1`: Summary for yesterday.
    - `/summary 2024-01-01`: Summary for a specific date.
- `/summary_history`: View a list of past summaries.

### 4.3 Interactive Menu (`/menu`)
The `/menu` command opens a graphical interface with buttons:

- **📊 Get 24h Summary**: Generates a summary of the last 24 hours immediately.
- **📈 Get 3-Day Summary**: Generates a summary of the last 3 days.
- **🔥 Generate Today's Summary**: Generates and **saves** the summary for the current day.
- **📋 View Saved Summaries**: Browse and read previously generated summaries.

### 4.4 AI Summaries
The bot can generate summaries in two ways:

1.  **Automatic (Daily)**:
    - Runs automatically at `AUTO_SUMMARY_TIME`.
    - Summarizes the previous day's chat.
    - Saves the summary to `data/summaries/`.

2.  **Manual (On-Demand)**:
    - Use `/menu` or `/summary` command.
    - Useful for catching up on recent discussions instantly.

## 5. Troubleshooting

### Bot not responding?
- Check if the process is running.
- Check `logs/telegram_notetaker.log` for errors.
- Ensure `TELEGRAM_BOT_TOKEN` is correct.

### "Permission Denied" for commands?
- Use `/myid` to get your ID.
- Add your ID to `ADMIN_IDS` in `.env`.
- Restart the bot.

### Summaries not generating?
- Ensure `ENABLE_AI_SUMMARY=true`.
- Check your API key balance/validity.
- Ensure the group has enough messages (default min: 10).

### How to find Group ID?
- Add the bot to the group.
- Send a message.
- Check the logs; the bot logs the `chat_id` of incoming messages.
