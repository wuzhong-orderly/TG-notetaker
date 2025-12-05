# Product Requirements Document (PRD): TG-notetaker

## 1. Introduction
**TG-notetaker** is a Telegram bot designed to automatically record, archive, and summarize group chat conversations. It aims to help users catch up on missed discussions and archive important information from Telegram groups.

## 2. Problem Statement
Telegram groups can generate a high volume of messages, making it difficult for users to keep up. Important information often gets lost in the noise. Users need a way to:
- Archive chat history for future reference.
- Get concise summaries of daily conversations.
- Search and retrieve past information easily.

## 3. Goals & Objectives
- **Automated Archiving**: Reliably record all text messages and media metadata from specified groups.
- **AI Summarization**: Provide intelligent daily and on-demand summaries of chat activities.
- **Privacy & Control**: Ensure only authorized groups are recorded and data is stored securely.
- **Ease of Use**: Simple commands and menu-driven interface for interaction.

## 4. User Personas
- **Group Admin**: Wants to archive group content and provide summaries for members.
- **Busy Professional**: Wants to catch up on group discussions quickly without reading hundreds of messages.
- **Researcher/Analyst**: Needs to archive and analyze community sentiment or discussions.

## 5. Functional Requirements

### 5.1 Message Recording
- **FR-1.1**: The bot MUST listen to all text messages in allowed groups.
- **FR-1.2**: The bot SHOULD record metadata for media messages (photos, videos, documents).
- **FR-1.3**: The bot MUST support multiple storage backends (JSON, Text, SQLite).
- **FR-1.4**: The bot MUST filter out messages from other bots or ignored commands.

### 5.2 AI Summarization
- **FR-2.1**: The bot MUST provide a daily automated summary of the previous day's chat.
- **FR-2.2**: The bot MUST allow admins to trigger a summary manually for a specific date or the last 24 hours.
- **FR-2.3**: The bot SHOULD support multiple AI providers (OpenAI, Anthropic, etc.).
- **FR-2.4**: Summaries SHOULD be customizable in length and language.

### 5.3 User Interaction
- **FR-3.1**: The bot MUST provide a `/start` command with usage instructions.
- **FR-3.2**: The bot MUST provide a `/menu` command for interactive feature access.
- **FR-3.3**: The bot MUST provide a `/stats` command to show group activity statistics.
- **FR-3.4**: The bot MUST restrict sensitive commands (like summarization) to admins.

### 5.5 Configuration & Deployment
- **FR-4.1**: The bot MUST be configurable via environment variables (`.env`).
- **FR-4.2**: The bot MUST support Docker for easy deployment.
- **FR-4.3**: The bot SHOULD allow configuring a whitelist of allowed groups.

## 6. Non-Functional Requirements
- **Reliability**: The bot should run continuously and handle network interruptions gracefully.
- **Performance**: Message recording should be asynchronous to not block the event loop.
- **Security**: API keys and tokens must be protected. Only authorized users should access admin features.
- **Scalability**: The system should handle moderately active groups (thousands of messages/day).

## 7. Future Scope
- **Web Interface**: A dashboard to view logs and summaries.
- **Search Functionality**: In-chat search for archived messages.
- **Sentiment Analysis**: Advanced analytics on group mood.
- **Multi-platform Support**: Support for Discord or Slack.
