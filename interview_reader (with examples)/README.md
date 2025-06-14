# Simple Interview Conversation Reader

A minimal tool to read and display TalentScout interview conversations.

## Purpose

This application focuses solely on displaying the conversation between the AI interviewer and the candidate in a clean, easy-to-read format.

## Features

- Simple listing of interview JSON files
- Clean conversation view with proper formatting for code blocks
- Automatic dark/light theme support based on system preferences
- Timestamps for each message
- Automatic scrolling to the latest message

## Usage

1. Run the application:
   ```
   python simple_reader.py
   ```

2. Open your browser:
   ```
   http://localhost:5001
   ```

3. Click on any interview file to view the conversation.

## Compatibility

This reader is designed to handle different interview JSON structures, including:
- `full_conversation` format
- `conversation_history` format 
- `conversation_transcript` format (with speaker/message structure)

## Requirements

- Flask
- Python 3.6+
