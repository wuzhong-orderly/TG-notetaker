# System Architecture: TG-notetaker

## 1. Overview
TG-notetaker is a Python-based application that acts as a Telegram bot. It is built using the `python-telegram-bot` library and follows a modular architecture to separate concerns between message handling, data storage, and AI processing.

## 2. High-Level Architecture

```mermaid
graph TD
    User[User/Group] -->|Messages| Bot[Bot Interface (bot.py)]
    Bot -->|Save| Storage[Storage Layer (storage.py)]
    Bot -->|Command| AI[AI Engine (ai_summary.py)]
    Scheduler[Scheduler (scheduler.py)] -->|Trigger| AI
    AI -->|Read| Storage
    AI -->|Summary| Bot
    Storage -->|Persist| FS[File System / SQLite]
```

## 3. Core Components

### 3.1 Bot Interface (`src/bot.py`)
The entry point of the application. It initializes the `Application` class from `python-telegram-bot`.
- **Responsibilities**:
    - Handles Telegram updates (messages, commands).
    - Authenticates users (Admin checks).
    - Routes commands to appropriate handlers.
    - Manages the `/menu` interactive interface.

### 3.2 Storage Layer (`src/storage.py`)
Abstracts the data persistence mechanism.
- **Supported Backends**:
    - **JSON**: Stores messages in daily JSON files per chat.
    - **Text**: Stores messages in human-readable text files.
    - **SQLite**: Stores messages in a relational database (for advanced querying).
- **Data Structure**:
    - Messages are normalized into a standard dictionary format before storage.

### 3.3 AI Engine (`src/ai_summary.py`)
Handles interactions with LLM providers (OpenAI, Anthropic).
- **Responsibilities**:
    - Fetches chat history from Storage.
    - Preprocesses text (filtering, formatting).
    - Constructs prompts for the LLM.
    - Calls the AI API and parses the response.
- **Key Features**:
    - Supports multiple models (GPT-4, Claude 3).
    - Configurable summary styles and languages.

### 3.4 Scheduler (`src/scheduler.py`)
Manages background tasks.
- **Responsibilities**:
    - Runs a daily job (default 00:00) to generate summaries for the previous day.
    - Ensures summaries are generated even if the bot restarts.

## 4. Data Flow

### 4.1 Message Recording
1.  User sends a message in a group.
2.  `bot.py` receives the `Update`.
3.  Checks if the group is allowed.
4.  Extracts message data (text, user info, timestamp).
5.  Calls `storage.save_message()`.
6.  Data is written to `data/messages/{chat_id}/{date}.json`.

### 4.2 AI Summarization
1.  **Trigger**:
    - **Auto**: Scheduler triggers at configured time.
    - **Manual**: Admin sends `/summary` command.
2.  `ai_summary.py` requests messages for the target date from `storage.py`.
3.  Messages are formatted into a prompt context.
4.  Prompt is sent to OpenAI/Anthropic API.
5.  Generated summary is returned.
6.  Summary is saved to `data/summaries/` and sent to the chat (if configured).

## 5. Directory Structure
- `src/`: Source code.
- `config/`: Configuration files.
- `data/`: Persistent data (messages, summaries).
- `logs/`: Application logs.

## 6. Technologies
- **Language**: Python 3.8+
- **Framework**: `python-telegram-bot`
- **AI**: OpenAI API / Anthropic API
- **Database**: SQLite (optional), JSON (default)
- **Deployment**: Docker / Docker Compose
