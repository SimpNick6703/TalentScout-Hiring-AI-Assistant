# TalentScout AI Hiring Assistant

## Overview

TalentScout is an AI-powered conversational hiring assistant designed to automate and streamline the technical interview process for software development positions. The assistant conducts structured, conversational interviews, gathering candidate information and assessing technical skills through a friendly, one-question-at-a-time approach.

## Features

- **Conversational Interview Flow**: Conducts natural, friendly conversations with candidates
- **Progressive Interview Phases**: 
  - Greeting
  - Information gathering
  - Technical assessment
  - Experience discussion
  - Project deep dive
  - Cultural fit assessment
  - Candidate questions
  - Next steps
- **Smart Data Extraction**: Automatically extracts candidate information from natural conversation
- **Responsive UI**: Clean interface with automatic light/dark theme switching
- **Data Export**: Complete interview data export in JSON format for further analysis
- **Provider-Agnostic**: Configurable to work with different LLM providers

## Project Structure

```
├── app.py                 # Main application file with Flask routes and UI
├── chatbot.py             # Core chatbot implementation and interview logic
├── config.py              # Configuration settings for the application
├── data_handler.py        # Data processing and storage utilities
├── requirements.txt       # Project dependencies
├── utils.py               # Utility functions
├── interview_reader/      # Tool for reading exported interview data (separate application)
└── static/                # Static assets
    └── styles.css         # CSS styling for the application
```

## Technical Stack

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript
- **AI Integration**: OpenAI Python SDK (compatible with LM Studio)
- **Data Handling**: JSON storage for interviews

## Installation and Setup

1. Clone the repository
```
git clone https://github.com/SimpNick6703/TalentScout-Hiring-AI-Assistant.git
```
2. Install dependencies:
```
pip install -r requirements.txt
```
3. Configure LLM settings in `config.py`:
   - Set appropriate `base_url` and `api_key` in the `OPENAI_CONFIG` section
   - Adjust model parameters as needed

4. Run the application:
```
streamlit run app.py
```

## Interview Flow

The interview follows a structured flow:

1. **Greeting**: Welcomes candidate and requests basic information
2. **Information Gathering**: Collects candidate information (name, email, phone, etc.)
3. **Technical Assessment**: Asks relevant technical questions based on candidate's tech stack
4. **Experience Discussion**: Explores professional experience
5. **Project Deep Dive**: Discusses technical project details
6. **Cultural Fit**: Assesses work style and team fit
7. **Candidate Questions**: Allows candidate to ask questions
8. **Next Steps**: Concludes the interview with follow-up information

## Exported Data Structure

Interviews are exported as JSON files with the following structure:

```json
{
  "interview_metadata": {
    "timestamp": "ISO-formatted date-time",
    "total_messages": "count",
    "current_phase": "phase name",
    "phase_index": "number",
    "technical_questions_asked": "count",
    "interview_completed": "boolean"
  },
  "candidate_information": {
    "name": "Candidate's full name",
    "email": "Email address",
    "phone": "Contact number with proper formatting",
    "experience": "Years of experience",
    "position": "Target position",
    "location": "Current location",
    "tech_stack": "Technologies and skills"
  },
  "conversation_history": [
    {
      "role": "assistant/user",
      "content": "message content",
      "timestamp": "ISO-formatted date-time"
    }
  ],
  "interview_analysis": {
    "missing_fields": ["any fields not collected"],
    "completion_percentage": "percentage complete",
    "phases_completed": "count",
    "total_phases": "count"
  }
}
```

## Interview Reader Tool

A separate tool for reading and analyzing exported interview data is available in the `interview_reader/` directory. This tool provides a simple interface for viewing exported interviews.

## Configuration Options

Adjust the application behavior in `config.py`:

- **OpenAI Configuration**: Connection details and model parameters
- **UI Theme**: Customize the appearance
- **Conversation Flow**: Adjust required fields, question counts, etc.
- **Technical Questions**: Customize the question database by topic

## License

This project is proprietary and confidential.
