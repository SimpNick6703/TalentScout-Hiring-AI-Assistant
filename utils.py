"""
Utility Functions
Helper functions for validation, data processing, and technical questions.
"""

import re
import json
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime

def validate_email(email: str) -> bool:
    """Validate email address format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))

def validate_phone(phone: str) -> bool:
    """Validate phone number format with specific support for Indian numbers (+91)"""
    # Remove common separators and spaces
    cleaned = re.sub(r'[-.\s\(\)]', '', phone)
    
    # Check for valid patterns with extra support for Indian numbers
    patterns = [
        # Indian mobile numbers (with +91 prefix)
        r'^\+91[6-9]\d{9}$',  
        # Indian mobile numbers (without prefix, starting with 6-9)
        r'^[6-9]\d{9}$',  
        # International format for other countries
        r'^\+\d{1,3}\d{8,12}$',
        # General 10-11 digit formats
        r'^\d{10}$',
        r'^\d{11}$'  
    ]
    
    return any(re.match(pattern, cleaned) for pattern in patterns)

def normalize_tech_stack(tech_list: List[str]) -> List[str]:
    """Normalize and standardize technology names"""
    tech_mapping = {
        'js': 'javascript',
        'ts': 'typescript',
        'py': 'python',
        'nodejs': 'node.js',
        'reactjs': 'react',
        'vuejs': 'vue',
        'angularjs': 'angular',
        'postgres': 'postgresql',
        'mongo': 'mongodb',
        'k8s': 'kubernetes',
        'tf': 'terraform',
        'aws lambda': 'aws',
        'ec2': 'aws',
        's3': 'aws',
        'azure functions': 'azure',
        'gcp': 'google cloud',
        'ml': 'machine learning',
        'ai': 'artificial intelligence',
        'dl': 'deep learning'
    }
    
    normalized = []
    for tech in tech_list:
        tech_lower = tech.lower().strip()
        normalized_tech = tech_mapping.get(tech_lower, tech_lower)
        if normalized_tech not in normalized:
            normalized.append(normalized_tech)
    
    return normalized

def extract_years_of_experience(text: str) -> Optional[int]:
    """Extract years of experience from text"""
    patterns = [
        r'(\d+)\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)',
        r'(\d+)\s*(?:years?|yrs?)',
        r'(\d+)\+?\s*(?:years?|yrs?)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            years = int(match.group(1))
            if 0 <= years <= 50:  # Reasonable range
                return years
    
    return None

def load_tech_questions() -> Dict[str, List[str]]:
    """Load technical questions from JSON file or return default questions"""
    questions_file = "tech_questions.json"
    
    if os.path.exists(questions_file):
        try:
            with open(questions_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    
    # Default questions if file doesn't exist
    return {
        "python": [
            "What are Python decorators and how do you use them?",
            "Explain the difference between list and tuple in Python.",
            "How does memory management work in Python?",
            "What is the Global Interpreter Lock (GIL) in Python?",
            "Explain Python's duck typing concept."
        ],
        "javascript": [
            "Explain the concept of closures in JavaScript.",
            "What is the difference between let, var, and const?",
            "How does the event loop work in JavaScript?",
            "What are promises and how do they work?",
            "Explain the difference between == and === operators."
        ],
        "react": [
            "What is the virtual DOM and how does it work?",
            "Explain the component lifecycle in React.",
            "What are React hooks and why are they useful?",
            "How do you handle state management in React?",
            "What is the difference between controlled and uncontrolled components?"
        ],
        "node.js": [
            "What is the event-driven architecture in Node.js?",
            "Explain the difference between process.nextTick() and setImmediate().",
            "How do you handle errors in Node.js?",
            "What are streams in Node.js?",
            "Explain the concept of clustering in Node.js."
        ],
        "django": [
            "Explain Django's MTV architecture.",
            "What are Django migrations and how do they work?",
            "How does Django's ORM work?",
            "What is middleware in Django?",
            "Explain Django's authentication system."
        ],
        "sql": [
            "What is the difference between INNER JOIN and LEFT JOIN?",
            "Explain database normalization and its forms.",
            "What are indexes and how do they improve performance?",
            "What is a stored procedure?",
            "Explain ACID properties in databases."
        ],
        "aws": [
            "What is the difference between EC2 and Lambda?",
            "Explain AWS S3 storage classes.",
            "What is Auto Scaling in AWS?",
            "How does AWS IAM work?",
            "What is the difference between EBS and EFS?"
        ],
        "docker": [
            "What is the difference between a Docker image and container?",
            "Explain Docker layers and how they work.",
            "What is a Dockerfile and its key instructions?",
            "How do you manage data persistence in Docker?",
            "What is Docker Compose and when would you use it?"
        ],
        "kubernetes": [
            "What are pods in Kubernetes?",
            "Explain the difference between Deployment and StatefulSet.",
            "What is a Kubernetes service?",
            "How does Kubernetes handle scaling?",
            "What are ConfigMaps and Secrets in Kubernetes?"
        ],
        "java": [
            "Explain the difference between JVM, JRE, and JDK.",
            "What are the principles of Object-Oriented Programming in Java?",
            "How does garbage collection work in Java?",
            "What is the difference between ArrayList and LinkedList?",
            "Explain Java's memory model and heap structure."
        ],
        "angular": [
            "What is dependency injection in Angular?",
            "Explain the difference between components and directives.",
            "How does change detection work in Angular?",
            "What are Angular services and how do you use them?",
            "Explain the Angular component lifecycle."
        ],
        "vue": [
            "What is the Vue.js reactivity system?",
            "Explain the difference between computed properties and methods.",
            "How do you handle component communication in Vue.js?",
            "What is Vuex and when would you use it?",
            "Explain Vue.js lifecycle hooks."
        ]
    }

def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent injection attacks"""
    if not isinstance(text, str):
        text = str(text)
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', text)
    
    # Limit length
    sanitized = sanitized[:1000]
    
    # Strip whitespace
    sanitized = sanitized.strip()
    
    return sanitized

def format_tech_stack_display(tech_stack: List[str]) -> str:
    """Format tech stack for display"""
    if not tech_stack:
        return "Not specified"
    
    # Capitalize first letter of each technology
    formatted = [tech.title() for tech in tech_stack]
    
    if len(formatted) <= 3:
        return ", ".join(formatted)
    else:
        return ", ".join(formatted[:3]) + f" and {len(formatted) - 3} more"

def calculate_experience_level(years: int) -> str:
    """Calculate experience level based on years"""
    if years == 0:
        return "Entry Level"
    elif 1 <= years <= 2:
        return "Junior"
    elif 3 <= years <= 5:
        return "Mid-Level"
    elif 6 <= years <= 10:
        return "Senior"
    else:
        return "Expert/Lead"

def generate_interview_summary(candidate_data: Dict) -> str:
    """Generate a formatted interview summary"""
    summary = "## Interview Summary\n\n"
    
    # Basic information
    if 'name' in candidate_data:
        summary += f"**Candidate:** {candidate_data['name']}\n"
    
    if 'position' in candidate_data:
        summary += f"**Position:** {candidate_data['position']}\n"
    
    if 'experience' in candidate_data:
        years = candidate_data['experience']
        level = calculate_experience_level(years)
        summary += f"**Experience:** {years} years ({level})\n"
    
    if 'location' in candidate_data:
        summary += f"**Location:** {candidate_data['location']}\n"
    
    # Technical skills
    if 'tech_stack' in candidate_data:
        tech_display = format_tech_stack_display(candidate_data['tech_stack'])
        summary += f"**Tech Stack:** {tech_display}\n"
    
    summary += f"\n**Interview Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    
    return summary

def detect_programming_languages(text: str) -> List[str]:
    """Detect programming languages mentioned in text"""
    languages = [
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust',
        'ruby', 'php', 'swift', 'kotlin', 'scala', 'perl', 'r', 'matlab',
        'objective-c', 'shell', 'bash', 'powershell', 'sql', 'html', 'css'
    ]
    
    text_lower = text.lower()
    found_languages = []
    
    for lang in languages:
        if lang in text_lower:
            found_languages.append(lang)
    
    return found_languages

def detect_frameworks_tools(text: str) -> List[str]:
    """Detect frameworks and tools mentioned in text"""
    frameworks_tools = [
        'react', 'angular', 'vue', 'django', 'flask', 'spring', 'laravel',
        'express', 'fastapi', 'rails', 'asp.net', 'node.js', 'nextjs',
        'nuxt', 'gatsby', 'svelte', 'backbone', 'ember', 'jquery',
        'bootstrap', 'tailwind', 'material-ui', 'ant-design',
        'docker', 'kubernetes', 'jenkins', 'git', 'gitlab', 'github',
        'aws', 'azure', 'gcp', 'heroku', 'netlify', 'vercel',
        'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch',
        'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas'
    ]
    
    text_lower = text.lower()
    found_tools = []
    
    for tool in frameworks_tools:
        if tool in text_lower:
            found_tools.append(tool)
    
    return found_tools

def validate_candidate_data(data: Dict) -> Tuple[bool, List[str]]:
    """Validate candidate data and return validation status and errors"""
    errors = []
    
    # Required fields
    required_fields = ['name', 'email', 'experience']
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"Missing required field: {field}")
    
    # Email validation
    if 'email' in data and not validate_email(data['email']):
        errors.append("Invalid email format")
    
    # Phone validation (if provided)
    if 'phone' in data and data['phone'] and not validate_phone(data['phone']):
        errors.append("Invalid phone number format")
    
    # Experience validation
    if 'experience' in data:
        try:
            exp = int(data['experience'])
            if exp < 0 or exp > 50:
                errors.append("Experience must be between 0 and 50 years")
        except (ValueError, TypeError):
            errors.append("Experience must be a valid number")
    
    # Name validation
    if 'name' in data:
        name = str(data['name']).strip()
        if len(name) < 2:
            errors.append("Name must be at least 2 characters long")
        if not re.match(r'^[a-zA-Z\s]+$', name):
            errors.append("Name can only contain letters and spaces")
    
    return len(errors) == 0, errors

def create_export_data(candidate_data: Dict, conversation_history: List = None) -> Dict:
    """Create export-ready data structure"""
    export_data = {
        "candidate_information": candidate_data,
        "export_timestamp": datetime.now().isoformat(),
        "data_version": "1.0"
    }
    
    if conversation_history:
        export_data["conversation_history"] = conversation_history
    
    return export_data
