import openai
import json
import re
from typing import Dict, List, Optional
from datetime import datetime
from config import OPENAI_CONFIG

class HiringAssistant:
    def __init__(self):
        self.client = openai.OpenAI(
            base_url=OPENAI_CONFIG["base_url"],
            api_key=OPENAI_CONFIG["api_key"]
        )
        self.conversation_history = []
        self.current_step = 'greeting'
        self.candidate_data = {}
        self.required_fields = [
            'name', 'email', 'phone', 'experience', 
            'position', 'location', 'tech_stack'
        ]
        
        # Interview progress tracking
        self.interview_phases = [
            'greeting', 'information_gathering', 'technical_assessment', 
            'experience_discussion', 'project_deep_dive', 'cultural_fit',
            'candidate_questions', 'next_steps', 'completed'
        ]        
        self.current_phase_index = 0
        self.technical_questions_asked = 0
        self.max_technical_questions = 5
        self.interview_completed = False
          # Initialize with greeting message
        self._add_to_history('assistant', self.get_greeting())
        
    def get_greeting(self) -> str:
        return """👋 Hello! Welcome to TalentScout's AI Hiring Assistant!

I'm here to conduct your technical interview for a software development position. 

During our structured interview, I will:\n
• Gather your professional information and background\n
• Assess your technical skills through targeted questions\n
• Discuss your experience and project work\n
• Explore cultural fit and answer your questions\n

Let's start by getting to know you better! Could you please tell me your full name?"""

    def _get_current_phase(self) -> str:
        if self.current_phase_index < len(self.interview_phases):
            return self.interview_phases[self.current_phase_index]
        return 'completed'

    def _get_system_prompt(self) -> str:
        current_phase = self._get_current_phase()
        missing_info = [field for field in self.required_fields if field not in self.candidate_data]
        
        # Build conversational system prompt
        base_prompt = f"""You are TalentScout, an expert AI hiring assistant conducting a CONVERSATIONAL technical interview for a software development position.

CRITICAL INFORMATION GATHERING RULE
You MUST collect ALL required candidate information before proceeding to technical questions.

REQUIRED CANDIDATE INFORMATION (MUST COLLECT ALL):
- name: Full name of the candidate
- email: Professional email address  
- phone: Contact phone number
- experience: Years of professional experience
- position: Target role/position applying for
- location: Current location/availability
- tech_stack: Programming languages, frameworks, technologies

CURRENT STATUS:
- Interview Phase: {current_phase}
- Missing Information: {missing_info}
- Technical Questions Asked: {self.technical_questions_asked}/{self.max_technical_questions}

CONVERSATIONAL INTERVIEW STYLE:
1. INFORMATION FIRST: If ANY required information is missing, ask for it before technical questions
2. ONE QUESTION ONLY: Ask exactly ONE question per response - never multiple questions
3. KEEP IT SHORT: Your responses should be 1-2 sentences maximum
4. EXPECT SHORT ANSWERS: Candidates should give 30-50 word responses, not essays
5. BE CONVERSATIONAL: Sound friendly and natural, like chatting with a colleague
6. BRIEF ACKNOWLEDGMENT: Quick "Great!" or "Perfect!" before next question

TECHNICAL QUESTION GUIDELINES:
- Ask ONE specific, focused question at a time
- Make it practical: "How do you handle..." rather than "Explain everything about..."
- Expect concise answers (30-50 words)
- Follow up naturally based on their response
- Avoid complex multi-part questions

CURRENT PHASE FOCUS:
{self._get_phase_instructions(current_phase)}

CONVERSATION EXAMPLES:
GOOD: "Great! What's your email address?"
GOOD: "Perfect! How many years of experience do you have?"
GOOD: "Nice! How do you usually handle API rate limits?"
BAD: "Can you tell me about your experience with APIs, error handling, and also your projects?"
BAD: Asking multiple questions in one response
BAD: Long responses expecting detailed explanations

REMEMBER: Keep it conversational, ONE question at a time, expect SHORT answers!
Missing fields to collect: {missing_info}"""

        return base_prompt

    def _get_phase_instructions(self, phase: str) -> str:
        missing_fields = [field for field in self.required_fields if field not in self.candidate_data]
        remaining_questions = max(0, self.max_technical_questions - self.technical_questions_asked)
        tech_stack = self.candidate_data.get('tech_stack', 'not specified yet')
        experience = self.candidate_data.get('experience', 'unknown')
        
        instructions = {
            'greeting': f"""
            Welcome briefly and ask for their full name to start.
            Keep it short: 1-2 sentences maximum.
            Missing fields: {missing_fields}
            """,
            
            'information_gathering': f"""
            🚨 PRIORITY: Collect ALL missing candidate information systematically.
            Missing fields that MUST be collected: {missing_fields}
            - Ask for ONE missing field at a time conversationally
            - Keep questions short: "Great! What's your email?" or "Perfect! How many years of experience?"
            - Brief acknowledgment, then one focused question
            - DO NOT move to technical questions until ALL fields are complete
            """,
            
            'technical_assessment': f"""
            Now ask SHORT, focused technical questions based on their tech stack: {tech_stack}
            - Ask {remaining_questions} more technical questions, ONE at a time
            - Keep questions specific and practical: "How do you handle API timeouts?"
            - Expect 30-50 word answers, not essays
            - Follow up naturally based on their response
            - Adjust difficulty for {experience} experience level
            """,
            
            'experience_discussion': """
            Ask SHORT questions about their professional experience.
            Example: "What's been your most challenging project?" - expect brief answers.
            """,
            
            'project_deep_dive': """
            Ask ONE focused question about their key project.
            Example: "What was the trickiest technical decision you made?" - keep it conversational.
            """,
            
            'cultural_fit': """
            Ask brief questions about work style and fit.
            Example: "How do you prefer to work in a team?" - expect short responses.
            """,
            
            'candidate_questions': """
            Ask: "Do you have any questions about the role or company?" 
            Keep responses brief and helpful.
            """,
            
            'next_steps': """
            Briefly explain next steps and thank them.
            Keep it short and professional.
            """
        }
        
        return instructions.get(phase, "Continue the interview professionally.")

    def _generate_ai_response(self, user_input: str) -> str:
        try:
            # Prepare messages with full conversation history
            messages = [
                {"role": "system", "content": self._get_system_prompt()}
            ]
            
            # Add conversation history
            for msg in self.conversation_history:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Add current user input
            messages.append({"role": "user", "content": user_input})
            
            # Generate response
            response = self.client.chat.completions.create(
                model=OPENAI_CONFIG["model"],
                messages=messages,
                temperature=OPENAI_CONFIG["temperature"],
                max_tokens=OPENAI_CONFIG["max_tokens"]
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"I apologize, but I'm experiencing a technical issue. Could you please repeat your response? (Error: {str(e)})"

    def process_message(self, user_input: str) -> str:
        if not user_input.strip():
            return "I didn't receive any input. Could you please tell me more?"
        
        # Add user message to history
        self._add_to_history('user', user_input)
        
        # Extract information from user input
        self._simple_extract_information(user_input)
        
        # Generate AI response
        response = self._generate_ai_response(user_input)
        
        # Add assistant response to history
        self._add_to_history('assistant', response)
        
        # Update interview progress
        self._update_interview_progress()
        
        return response

    def process_message_stream(self, user_input: str):
        if not user_input.strip():
            yield "I didn't receive any input. Could you please tell me more?"
            return
        
        # Add user message to history
        self._add_to_history('user', user_input)
        
        # Extract information
        self._simple_extract_information(user_input)
        
        try:
            # Prepare messages
            messages = [
                {"role": "system", "content": self._get_system_prompt()}
            ]
            
            for msg in self.conversation_history:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            messages.append({"role": "user", "content": user_input})
            
            # Stream response
            response_text = ""
            stream = self.client.chat.completions.create(
                model=OPENAI_CONFIG["model"],
                messages=messages,
                temperature=OPENAI_CONFIG["temperature"],
                max_tokens=OPENAI_CONFIG["max_tokens"],
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    chunk_text = chunk.choices[0].delta.content
                    response_text += chunk_text
                    yield chunk_text
            
            # Add complete response to history
            self._add_to_history('assistant', response_text)
            self._update_interview_progress()
            
        except Exception as e:
            error_msg = f"I apologize, but I'm experiencing a technical issue. Could you please repeat your response? (Error: {str(e)})"
            yield error_msg
            self._add_to_history('assistant', error_msg)

    def _simple_extract_information(self, text: str):
        text_lower = text.lower()
        
        # Enhanced name extraction
        if not self.candidate_data.get('name'):
            # Look for "I'm", "my name is", "I am", etc.
            name_patterns = [
                r"(?:i'?m|my name is|i am|call me)\s+([a-zA-Z][a-zA-Z\s'-]{1,30}[a-zA-Z])",
                r"(?:hi|hello),?\s+(?:i'?m|my name is|i am)\s+([a-zA-Z][a-zA-Z\s'-]{1,30}[a-zA-Z])",
                r"^([a-zA-Z][a-zA-Z\s'-]{1,30}[a-zA-Z])(?:\s+here|\s*$|\s+speaking)"
            ]
            
            for pattern in name_patterns:
                match = re.search(pattern, text_lower)
                if match:
                    name = match.group(1).strip().title()
                    if len(name.split()) >= 1 and len(name) >= 2:
                        self.candidate_data['name'] = name
                        break
        
        # Enhanced email extraction
        if not self.candidate_data.get('email'):
            email_match = re.search(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b', text)
            if email_match:
                self.candidate_data['email'] = email_match.group()
        if not self.candidate_data.get('phone'):
            phone_patterns = [
                # Indian phone numbers with +91 prefix
                r'\+91[-\s]?([6-9][0-9]{9})\b',
                r'\+91[-\s]?([6-9][0-9]{4})[-\s]?([0-9]{5})\b',
                # Direct +91 format without space
                r'\b\+91([6-9][0-9]{9})\b',
                # Indian mobile numbers without country code
                r'\b([6-9][0-9]{9})\b',
                r'\b([6-9][0-9]{4})[-\s]?([0-9]{5})\b',
                # General formats with parentheses or separators
                r'\(([6-9][0-9]{4})\)[-\s]?([0-9]{5})\b',
                r'(?<!\+|\d)([6-9][0-9]{4})[-\s]?([0-9]{5})\b'
            ]
            
            for pattern in phone_patterns:
                match = re.search(pattern, text)
                if match:
                    # Standardize phone number format
                    if '+91' in pattern or '+91' in match.group():
                        # Format with +91 prefix
                        if len(match.groups()) == 1:
                            # Get the 10 digits
                            digits = match.group(1)
                            self.candidate_data['phone'] = f"+91 {digits[:5]} {digits[5:]}"
                        elif len(match.groups()) == 2:
                            self.candidate_data['phone'] = f"+91 {match.group(1)} {match.group(2)}"
                    else:
                        # Add +91 prefix for Indian numbers without it
                        if len(match.groups()) == 1:
                            digits = match.group(1)
                            self.candidate_data['phone'] = f"+91 {digits[:5]} {digits[5:]}"
                        elif len(match.groups()) == 2:
                            self.candidate_data['phone'] = f"+91 {match.group(1)} {match.group(2)}"
                    
                    # Validation check
                    phone_without_spaces = self.candidate_data['phone'].replace(' ', '')
                    if not re.match(r'^\+91[6-9][0-9]{9}$', phone_without_spaces):
                        # Fallback if format is still incorrect
                        cleaned_digits = re.sub(r'[^0-9]', '', match.group())
                        if len(cleaned_digits) == 10 and cleaned_digits[0] in '6789':
                            self.candidate_data['phone'] = f"+91 {cleaned_digits[:5]} {cleaned_digits[5:]}"
                    break
        
        # Enhanced experience extraction
        if not self.candidate_data.get('experience'):
            exp_patterns = [
                r'(\d+)(?:\+)?\s*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)',
                r'(?:experience|exp).*?(\d+)(?:\+)?\s*(?:years?|yrs?)',
                r'(?:been\s+(?:working|coding|developing|programming)).*?(\d+)(?:\+)?\s*(?:years?|yrs?)',
                r'(\d+)(?:\+)?\s*(?:years?|yrs?)\s*(?:in|as|doing)'
            ]
            
            for pattern in exp_patterns:
                match = re.search(pattern, text_lower)
                if match:
                    years = match.group(1)
                    self.candidate_data['experience'] = f"{years} years"
                    break
          # Enhanced position extraction - Improved for accuracy
        if not self.candidate_data.get('position'):
            position_keywords = [
                'developer', 'engineer', 'programmer', 'architect', 'analyst',
                'manager', 'lead', 'senior', 'junior', 'full stack', 'frontend', 'front-end', 'front end',
                'backend', 'back-end', 'back end', 'software', 'web', 'mobile', 'devops', 'qa', 'tester',
                'sde', 'data scientist', 'machine learning', 'ml', 'ai', 'cloud', 'security', 'administrator'
            ]
            
            for keyword in position_keywords:
                if keyword in text_lower:
                    # Find the surrounding context related to job position
                    patterns = [
                        # Direct job title references
                        rf'\b(?:as\s+(?:a\s+)?|i\'?m\s+(?:a\s+)?|i am\s+(?:a\s+)?|work\s+as\s+(?:a\s+)?|working\s+as\s+(?:a\s+)?)([^.!?]*{keyword}[^.!?]*)',
                        # Position/role references
                        rf'\b(?:position|role|job|title)\s+(?:is|as|:)?\s+([^.!?]*{keyword}[^.!?]*)',
                        # Application references
                        rf'\b(?:applying\s+for|interested\s+in|looking\s+for)\s+([^.!?]*{keyword}[^.!?]*)'
                    ]
                    
                    for pattern in patterns:
                        match = re.search(pattern, text_lower)
                        if match:
                            position = match.group(1).strip()
                            # Remove location phrases from positions
                            location_indicators = ['in', 'at', 'from', 'near', 'around']
                            for indicator in location_indicators:
                                loc_split = position.split(f" {indicator} ")
                                if len(loc_split) > 1:
                                    # Keep only the part before the location indicator
                                    position = loc_split[0].strip()
                            
                            # Limit length and ensure it's position-related
                            if 3 < len(position) < 50:
                                self.candidate_data['position'] = position.title()
                                break
                    
                    # If position was found in any pattern, break the keyword loop
                    if self.candidate_data.get('position'):
                        break
          # Enhanced location extraction - Improved for clarity and precision
        if not self.candidate_data.get('location'):
            # Common Indian and international locations for candidates
            common_locations = [
                'bangalore', 'bengaluru', 'mumbai', 'delhi', 'hyderabad', 'chennai', 'kolkata', 
                'pune', 'ahmedabad', 'noida', 'gurgaon', 'gurugram', 'new delhi', 'kochi', 
                'chandigarh', 'jaipur', 'indore', 'coimbatore', 'remote', 'work from home', 'wfh',
                'new york', 'london', 'singapore', 'dubai', 'australia', 'canada', 'usa', 'uk'
            ]
            
            # Check for common locations
            for loc in common_locations:
                if loc in text_lower:
                    if loc == 'wfh':
                        self.candidate_data['location'] = 'Work From Home'
                    else:
                        self.candidate_data['location'] = loc.title()
                    break
            
            # If common location not found, use refined patterns
            if not self.candidate_data.get('location'):
                location_patterns = [
                    # Explicit location statements
                    r'(?:i am|i\'m|am|currently|presently)\s+(?:from|in|at|living|based|located|residing)\s+(?:in\s+)?([A-Za-z\s,.-]+?)(?:\s*[.!?]|$|,)',
                    r'(?:my|current)\s+location\s+(?:is|:)\s+([A-Za-z\s,.-]+?)(?:\s*[.!?]|$|,)',
                    # Geographic references
                    r'(?:located|based|living)\s+(?:at|in|near)\s+([A-Za-z\s,.-]+?)(?:\s*[.!?]|$|,)',
                    # City/region with qualifiers
                    r'(?:city|town|region|area)\s+(?:of|is|:)\s+([A-Za-z\s,.-]+?)(?:\s*[.!?]|$|,)',
                    # Remote work statements
                    r'(?:i|working|available|prefer)\s+(?:to\s+)?(?:work\s+)?(?:remotely|remote\s+work|from\s+home|wfh)'
                ]
                
                for pattern in location_patterns:
                    match = re.search(pattern, text_lower)
                    if match:
                        if 'remote' in pattern or 'from home' in pattern or 'wfh' in pattern:
                            self.candidate_data['location'] = 'Work From Home'
                            break
                            
                        if match.groups():
                            location = match.group(1).strip()
                            # Filter out common filler phrases and ensure reasonable length
                            filler_words = ['the', 'a', 'an', 'or', 'and', 'but', 'from']
                            if (len(location) > 2 and 
                                not all(word in filler_words for word in location.split()) and 
                                len(location.split()) <= 4):
                                self.candidate_data['location'] = location.title()
                                break
        
        # Enhanced tech stack extraction
        if not self.candidate_data.get('tech_stack'):
            tech_keywords = [
                'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust',
                'react', 'angular', 'vue', 'node', 'express', 'spring', 'django', 'flask',
                'aws', 'azure', 'docker', 'kubernetes', 'jenkins', 'git', 'sql', 'nosql',
                'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch'
            ]
            
            found_techs = []
            for tech in tech_keywords:
                if tech in text_lower:
                    found_techs.append(tech.title())
            
            if found_techs:
                self.candidate_data['tech_stack'] = ', '.join(found_techs)

    def _update_interview_progress(self):
        missing_info = [field for field in self.required_fields if field not in self.candidate_data]
        
        # If in greeting phase and we have some info, move to information gathering
        if self.current_phase_index == 0 and len(self.candidate_data) > 0:
            self.current_phase_index = 1
        
        # If in information gathering and all info collected, move to technical
        elif self.current_phase_index == 1 and not missing_info:
            self.current_phase_index = 2
        
        # Progress through technical questions
        elif self.current_phase_index == 2 and self.technical_questions_asked >= self.max_technical_questions:
            self.current_phase_index = 3
          # Auto-progress through later phases (can be customized)
        elif self.current_phase_index >= 3:
            conversation_length = len(self.conversation_history)
            if conversation_length > 20:  # Move to next phase after several exchanges
                self.current_phase_index = min(self.current_phase_index + 1, len(self.interview_phases) - 1)
                
    def _add_to_history(self, role: str, content: str):
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
    def get_conversation_summary(self) -> Dict:
        # Validate required fields are present and correctly formatted
        self._validate_and_normalize_candidate_data()
        
        missing_fields = [field for field in self.required_fields if field not in self.candidate_data]
        
        return {
            "candidate_data": self.candidate_data,
            "conversation_length": len(self.conversation_history),
            "current_phase": self._get_current_phase(),
            "phase_index": self.current_phase_index,
            "technical_questions_asked": self.technical_questions_asked,
            "missing_information": missing_fields,
            "completion_percentage": ((len(self.required_fields) - len(missing_fields)) / len(self.required_fields)) * 100,
            "interview_completed": len(missing_fields) == 0 and self.current_phase_index >= 2
        }
        
    def _validate_and_normalize_candidate_data(self):
        # Ensure phone numbers have +91 prefix for Indian numbers
        if 'phone' in self.candidate_data:
            phone = self.candidate_data['phone']
            clean_phone = re.sub(r'[^0-9+]', '', phone)
            
            # Add +91 prefix if missing and is 10-digit Indian number
            if len(clean_phone) == 10 and clean_phone[0] in '6789':
                self.candidate_data['phone'] = f"+91 {clean_phone[:5]} {clean_phone[5:]}"
            elif clean_phone.startswith('+91') and len(clean_phone) == 13:
                # Format existing +91 number
                digits = clean_phone[3:]  # Skip +91
                self.candidate_data['phone'] = f"+91 {digits[:5]} {digits[5:]}"
        
        # Ensure location is properly formatted
        if 'location' in self.candidate_data:
            location = self.candidate_data['location']
            # Normalize "work from home" variations
            if re.search(r'(remote|work\s*from\s*home|wfh)', location.lower()):
                self.candidate_data['location'] = "Work From Home"
            else:
                # Title case for locations
                self.candidate_data['location'] = location.title()

    def export_interview_data(self, filename: str = None) -> str:
        if not filename:
            # Include candidate name if available
            name_part = self.candidate_data.get('name', '').split()[0] if self.candidate_data.get('name') else ''
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"interview_{name_part}_{timestamp}.json" if name_part else f"interview_export_{timestamp}.json"
        
        # Ensure candidate data is validated before export
        self._validate_and_normalize_candidate_data()
        
        export_data = {
            "interview_metadata": {
                "timestamp": datetime.now().isoformat(),
                "total_messages": len(self.conversation_history),
                "current_phase": self._get_current_phase(),
                "phase_index": self.current_phase_index,
                "technical_questions_asked": self.technical_questions_asked,
                "interview_completed": self.current_phase_index >= 2 and len([f for f in self.required_fields if f not in self.candidate_data]) == 0
            },
            "candidate_information": self.candidate_data,
            "conversation_history": self.conversation_history,
            "interview_analysis": {
                "missing_fields": [field for field in self.required_fields if field not in self.candidate_data],
                "completion_percentage": ((len(self.required_fields) - len([f for f in self.required_fields if f not in self.candidate_data])) / len(self.required_fields)) * 100,
                "phases_completed": self.current_phase_index + 1,
                "total_phases": len(self.interview_phases)
            }
        }
        
        # Verify all required fields are populated before export
        self._verify_export_completeness(export_data)
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            return f"Interview data exported to {filename}"
        except Exception as e:
            return f"Export failed: {str(e)}"
        
    def _verify_export_completeness(self, export_data: Dict) -> None:
        candidate_info = export_data.get("candidate_information", {})
        
        # Check for critical fields and ensure proper formatting
        
        # 1. Phone number validation and standardization
        if 'phone' in candidate_info:
            phone = candidate_info['phone']
            clean_digits = re.sub(r'[^0-9+]', '', phone)
            
            # Ensure standard format of "+91 XXXXX XXXXX" for Indian numbers
            if clean_digits.startswith('+91') and len(clean_digits) >= 13:
                # Already has +91, just format properly
                digits = clean_digits[3:]  # Remove +91
                candidate_info['phone'] = f"+91 {digits[:5]} {digits[5:]}"
            elif len(clean_digits) == 10 and clean_digits[0] in '6789':
                # 10-digit Indian number without +91 prefix
                candidate_info['phone'] = f"+91 {clean_digits[:5]} {clean_digits[5:]}"
            elif re.match(r'^[6-9]\d{9}$', re.sub(r'[^0-9]', '', phone)):
                # Another form of 10-digit number
                digits = re.sub(r'[^0-9]', '', phone)
                candidate_info['phone'] = f"+91 {digits[:5]} {digits[5:]}"
        
        # 2. Location normalization
        if 'location' in candidate_info:
            location = candidate_info['location']
            
            # Standardize "work from home" variations
            if re.search(r'(?i)(remote|wfh|work\s*from\s*home)', location):
                candidate_info['location'] = "Work From Home"
            else:
                # Proper title case for locations
                candidate_info['location'] = ' '.join(
                    word.capitalize() if word.lower() not in ['of', 'the', 'in', 'at', 'and', 'or'] 
                    else word.lower() for word in location.split()
                )
            
            # Ensure location doesn't have extraneous words or punctuation
            candidate_info['location'] = re.sub(r'[^\w\s]$', '', candidate_info['location']).strip()
        
        # 3. Other critical fields check
        for field in self.required_fields:
            if field not in candidate_info:
                # If a required field is missing, add a placeholder to indicate it
                candidate_info[field] = "[Not Provided]"
            elif not candidate_info[field]:
                # If field is empty, add placeholder
                candidate_info[field] = "[Not Provided]"