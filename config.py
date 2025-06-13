"""
Configuration settings for the TalentScout Hiring Assistant.
"""

import os
from typing import Dict, List

# Application Settings
APP_CONFIG = {
    "title": "TalentScout - AI Hiring Assistant",
    "description": "Intelligent chatbot for technology candidate screening",
    "version": "1.0.0",
    "author": "TalentScout Team"
}

# OpenAI Configuration for LM Studio
OPENAI_CONFIG = {
    "base_url": "http://127.0.0.1:1234/v1",
    "api_key": "lm-studio",
    "model": "local-model",
    "max_tokens": 4096,
    "temperature": 0.7
}

# Streamlit Configuration
STREAMLIT_CONFIG = {
    "page_title": APP_CONFIG["title"],
    "page_icon": "🤖",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Data Storage Configuration
DATA_CONFIG = {
    "data_directory": "data",
    "candidates_file": "candidates.json",
    "sessions_file": "sessions.json",
    "retention_days": 730,  # 2 years for GDPR compliance
    "max_file_size_mb": 10
}

# Conversation Flow Configuration
CONVERSATION_CONFIG = {
    "required_fields": [
        "name", "email", "phone", "experience", 
        "position", "location", "tech_stack"
    ],
    "max_technical_questions": 5,
    "min_technical_questions": 3,
    "conversation_timeout_minutes": 30,
    "max_message_length": 1000
}

# Validation Rules
VALIDATION_RULES = {
    "name": {
        "min_length": 2,
        "max_length": 100,
        "pattern": r'^[a-zA-Z\s\-\'\.]+$'
    },
    "email": {
        "pattern": r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    },
    "phone": {
        "patterns": [
            r'^\d{10}$',  # 10 digits
            r'^\+\d{1,3}\d{10,}$',  # International
            r'^\d{11}$'  # 11 digits
        ]
    },
    "experience": {
        "min_value": 0,
        "max_value": 50
    },
    "position": {
        "min_length": 2,
        "max_length": 100
    },
    "location": {
        "min_length": 2,
        "max_length": 100
    }
}

# Technical Skills Categories
TECH_CATEGORIES = {
    "programming_languages": [
        "python", "java", "javascript", "typescript", "c++", "c#", "go", 
        "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "matlab"
    ],
    "web_frameworks": [
        "react", "angular", "vue", "django", "flask", "spring", "laravel", 
        "express", "fastapi", "rails", "asp.net", "nextjs", "nuxt"
    ],
    "databases": [
        "mysql", "postgresql", "mongodb", "redis", "elasticsearch", 
        "cassandra", "dynamodb", "sqlite", "oracle", "sql-server"
    ],
    "cloud_platforms": [
        "aws", "azure", "gcp", "heroku", "netlify", "vercel", "digitalocean"
    ],
    "devops_tools": [
        "docker", "kubernetes", "jenkins", "gitlab-ci", "github-actions", 
        "terraform", "ansible", "chef", "puppet"
    ],
    "data_science": [
        "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", 
        "numpy", "matplotlib", "jupyter", "spark", "hadoop"
    ]
}

# Technical Questions Database
TECHNICAL_QUESTIONS = {
    "python": [
        "What are Python decorators and how do you use them?",
        "Explain the difference between list and tuple in Python.",
        "How does memory management work in Python?",
        "What is the Global Interpreter Lock (GIL) in Python?",
        "Explain Python's duck typing concept.",
        "How do you handle exceptions in Python?",
        "What are Python generators and when would you use them?",
        "Explain the difference between @staticmethod and @classmethod."
    ],
    "javascript": [
        "Explain the concept of closures in JavaScript.",
        "What is the difference between let, var, and const?",
        "How does the event loop work in JavaScript?",
        "What are promises and how do they work?",
        "Explain the difference between == and === operators.",
        "What is hoisting in JavaScript?",
        "How do you handle asynchronous operations in JavaScript?",
        "Explain the 'this' keyword in different contexts."
    ],
    "react": [
        "What is the virtual DOM and how does it work?",
        "Explain the component lifecycle in React.",
        "What are React hooks and why are they useful?",
        "How do you handle state management in React?",
        "What is the difference between controlled and uncontrolled components?",
        "Explain React's reconciliation process.",
        "How do you optimize performance in React applications?",
        "What are higher-order components (HOCs)?"
    ],
    "java": [
        "Explain the difference between JVM, JRE, and JDK.",
        "What are the principles of Object-Oriented Programming in Java?",
        "How does garbage collection work in Java?",
        "What is the difference between ArrayList and LinkedList?",
        "Explain Java's memory model and heap structure.",
        "What are Java generics and why are they useful?",
        "How do you handle multithreading in Java?",
        "Explain the difference between checked and unchecked exceptions."
    ],
    "sql": [
        "What is the difference between INNER JOIN and LEFT JOIN?",
        "Explain database normalization and its forms.",
        "What are indexes and how do they improve performance?",
        "What is a stored procedure?",
        "Explain ACID properties in databases.",
        "How do you optimize slow SQL queries?",
        "What is the difference between DELETE, TRUNCATE, and DROP?",
        "Explain the concept of database transactions."
    ],
    "aws": [
        "What is the difference between EC2 and Lambda?",
        "Explain AWS S3 storage classes.",
        "What is Auto Scaling in AWS?",
        "How does AWS IAM work?",
        "What is the difference between EBS and EFS?",
        "Explain AWS VPC and its components.",
        "How do you monitor AWS resources?",
        "What are the different AWS database services?"
    ],
    "docker": [
        "What is the difference between a Docker image and container?",
        "Explain Docker layers and how they work.",
        "What is a Dockerfile and its key instructions?",
        "How do you manage data persistence in Docker?",
        "What is Docker Compose and when would you use it?",
        "How do you optimize Docker images for production?",
        "Explain Docker networking concepts.",
        "What are Docker volumes and bind mounts?"
    ],
    "kubernetes": [
        "What are pods in Kubernetes?",
        "Explain the difference between Deployment and StatefulSet.",
        "What is a Kubernetes service?",
        "How does Kubernetes handle scaling?",
        "What are ConfigMaps and Secrets in Kubernetes?",
        "Explain Kubernetes networking and ingress.",
        "How do you monitor Kubernetes clusters?",
        "What are Kubernetes namespaces and why use them?"
    ]
}

# UI Theme Configuration (Dark Mode)
UI_THEME = {
    "primary_color": "#3182ce",
    "background_color": "#0c0c0c",
    "secondary_background": "#1a1a1a",
    "card_background": "#2d3748",
    "text_color": "#ffffff",
    "secondary_text": "#a0aec0",
    "accent_color": "#63b3ed",
    "success_color": "#38a169",
    "warning_color": "#ed8936",
    "error_color": "#e53e3e",
    "border_color": "#4a5568"
}

# Message Templates
MESSAGE_TEMPLATES = {
    "greeting": """
👋 Hello! Welcome to TalentScout's AI Hiring Assistant!

I'm here to help with your initial screening process for technology positions. 

During our conversation, I'll:
• Gather your basic information and experience
• Learn about your technical skills and preferred tech stack
• Ask relevant technical questions based on your expertise
• Provide information about next steps

This process typically takes 10-15 minutes. Let's get started!

Could you please tell me your full name?
    """,
    
    "completion": """
Excellent! You've completed all the technical questions. 

🎉 **Interview Summary:**
• Personal information collected ✓
• Technical skills assessed ✓
• Questions answered ✓

**Next Steps:**
1. Our technical team will review your responses
2. You'll receive feedback within 2-3 business days
3. Successful candidates will be invited for a detailed interview

Thank you for your time and interest in our company! 

Feel free to type 'bye' to end the conversation, or ask any questions about the process.
    """,
    
    "fallback": """
I appreciate your response. Let me ask you another question to better understand your background.
    """,
    
    "error": """
I'm sorry, I didn't quite understand that. Could you please rephrase your response?
    """
}

# Privacy and Security Settings
PRIVACY_CONFIG = {
    "data_encryption": True,
    "anonymize_data": True,
    "gdpr_compliance": True,
    "data_retention_days": 730,
    "consent_required": True,
    "audit_logging": True
}

# Performance Settings
PERFORMANCE_CONFIG = {
    "cache_responses": True,
    "max_conversation_length": 50,
    "response_timeout_seconds": 30,
    "max_concurrent_sessions": 100
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "app.log",
    "max_file_size": "10MB",
    "backup_count": 5
}

# Environment-specific settings
def get_config():
    """Get configuration based on environment"""
    env = os.getenv("ENVIRONMENT", "development")
    
    if env == "production":
        return {
            **OPENAI_CONFIG,
            "debug": False,
            "log_level": "WARNING"
        }
    else:
        return {
            **OPENAI_CONFIG,
            "debug": True,
            "log_level": "DEBUG"
        }
