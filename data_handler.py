"""
Data Handler Module
Manages candidate data storage, validation, and privacy compliance.
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Optional
import hashlib
import uuid

class DataHandler:
    """
    Handles data storage, validation, and privacy for candidate information.
    Ensures GDPR compliance and secure data handling.
    """
    
    def __init__(self, data_dir: str = "data"):
        """Initialize data handler with storage directory"""
        self.data_dir = data_dir
        self.candidates_file = os.path.join(data_dir, "candidates.json")
        self.sessions_file = os.path.join(data_dir, "sessions.json")
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize data files if they don't exist
        self._initialize_data_files()
    
    def _initialize_data_files(self):
        """Initialize data files with empty structures"""
        if not os.path.exists(self.candidates_file):
            with open(self.candidates_file, 'w') as f:
                json.dump([], f)
        
        if not os.path.exists(self.sessions_file):
            with open(self.sessions_file, 'w') as f:
                json.dump([], f)
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_phone(self, phone: str) -> bool:
        """Validate phone number format"""
        # Remove common separators and spaces
        cleaned = re.sub(r'[-.\s\(\)]', '', phone)
        
        # Check for valid patterns
        patterns = [
            r'^\d{10}$',  # 10 digits
            r'^\+\d{1,3}\d{10,}$',  # International format
            r'^\d{11}$'  # 11 digits (with country code)
        ]
        
        return any(re.match(pattern, cleaned) for pattern in patterns)
    
    def sanitize_data(self, data: Dict) -> Dict:
        """Sanitize and validate candidate data"""
        sanitized = {}
        
        # Name validation and sanitization
        if 'name' in data:
            name = str(data['name']).strip()
            if len(name) >= 2 and name.replace(' ', '').isalpha():
                sanitized['name'] = name.title()
        
        # Email validation
        if 'email' in data:
            email = str(data['email']).strip().lower()
            if self.validate_email(email):
                sanitized['email'] = email
        
        # Phone validation
        if 'phone' in data:
            phone = str(data['phone']).strip()
            if self.validate_phone(phone):
                sanitized['phone'] = phone
        
        # Experience validation
        if 'experience' in data:
            try:
                exp = int(data['experience'])
                if 0 <= exp <= 50:  # Reasonable experience range
                    sanitized['experience'] = exp
            except (ValueError, TypeError):
                pass
        
        # Position sanitization
        if 'position' in data:
            position = str(data['position']).strip()
            if len(position) >= 2:
                sanitized['position'] = position.title()
        
        # Location sanitization
        if 'location' in data:
            location = str(data['location']).strip()
            if len(location) >= 2:
                sanitized['location'] = location.title()
        
        # Tech stack validation
        if 'tech_stack' in data:
            if isinstance(data['tech_stack'], list):
                tech_stack = [str(tech).strip().lower() for tech in data['tech_stack'] if tech]
                sanitized['tech_stack'] = tech_stack
        
        return sanitized
    
    def generate_candidate_id(self, candidate_data: Dict) -> str:
        """Generate unique candidate ID based on email and timestamp"""
        email = candidate_data.get('email', '')
        timestamp = datetime.now().isoformat()
        
        # Create hash for anonymization
        hash_input = f"{email}_{timestamp}".encode('utf-8')
        candidate_id = hashlib.sha256(hash_input).hexdigest()[:12]
        
        return f"CAND_{candidate_id}"
    
    def anonymize_data(self, data: Dict) -> Dict:
        """Anonymize sensitive data for storage"""
        anonymized = data.copy()
        
        # Hash email for privacy
        if 'email' in anonymized:
            email_hash = hashlib.sha256(anonymized['email'].encode()).hexdigest()[:16]
            anonymized['email_hash'] = email_hash
            del anonymized['email']  # Remove original email
        
        # Partially mask phone number
        if 'phone' in anonymized:
            phone = str(anonymized['phone'])
            if len(phone) >= 10:
                masked = phone[:3] + '*' * (len(phone) - 6) + phone[-3:]
                anonymized['phone_masked'] = masked
                del anonymized['phone']  # Remove original phone
        
        return anonymized
    
    def save_candidate_data(self, candidate_data: Dict, session_id: str = None) -> str:
        """Save candidate data with privacy compliance"""
        try:
            # Sanitize data
            sanitized_data = self.sanitize_data(candidate_data)
            
            if not sanitized_data:
                raise ValueError("No valid data to save")
            
            # Generate candidate ID
            candidate_id = self.generate_candidate_id(sanitized_data)
            
            # Prepare data for storage
            storage_data = {
                'candidate_id': candidate_id,
                'session_id': session_id or str(uuid.uuid4()),
                'timestamp': datetime.now().isoformat(),
                'data': self.anonymize_data(sanitized_data),
                'data_retention_date': self._calculate_retention_date(),
                'consent_given': True  # In real app, this would be explicit
            }
            
            # Load existing candidates
            candidates = self._load_candidates()
            
            # Add new candidate
            candidates.append(storage_data)
            
            # Save to file
            with open(self.candidates_file, 'w') as f:
                json.dump(candidates, f, indent=2, default=str)
            
            return candidate_id
        
        except Exception as e:
            print(f"Error saving candidate data: {e}")
            return None
    
    def _load_candidates(self) -> List[Dict]:
        """Load candidates from storage"""
        try:
            with open(self.candidates_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _calculate_retention_date(self) -> str:
        """Calculate data retention date (GDPR compliance - 2 years)"""
        from datetime import timedelta
        retention_date = datetime.now() + timedelta(days=730)  # 2 years
        return retention_date.isoformat()
    
    def get_candidate_data(self, candidate_id: str) -> Optional[Dict]:
        """Retrieve candidate data by ID"""
        candidates = self._load_candidates()
        
        for candidate in candidates:
            if candidate.get('candidate_id') == candidate_id:
                return candidate
        
        return None
    
    def delete_candidate_data(self, candidate_id: str) -> bool:
        """Delete candidate data (GDPR right to be forgotten)"""
        try:
            candidates = self._load_candidates()
            
            # Filter out the candidate to delete
            updated_candidates = [
                c for c in candidates 
                if c.get('candidate_id') != candidate_id
            ]
            
            if len(updated_candidates) < len(candidates):
                # Save updated list
                with open(self.candidates_file, 'w') as f:
                    json.dump(updated_candidates, f, indent=2, default=str)
                return True
            
            return False
        
        except Exception as e:
            print(f"Error deleting candidate data: {e}")
            return False
    
    def cleanup_expired_data(self):
        """Clean up expired data based on retention policy"""
        try:
            candidates = self._load_candidates()
            current_time = datetime.now()
            
            # Filter out expired data
            valid_candidates = []
            for candidate in candidates:
                retention_date = datetime.fromisoformat(candidate.get('data_retention_date', ''))
                if retention_date > current_time:
                    valid_candidates.append(candidate)
            
            # Save cleaned data
            with open(self.candidates_file, 'w') as f:
                json.dump(valid_candidates, f, indent=2, default=str)
            
            print(f"Cleaned up {len(candidates) - len(valid_candidates)} expired records")
        
        except Exception as e:
            print(f"Error during data cleanup: {e}")
    
    def export_candidate_data(self, candidate_id: str) -> Optional[str]:
        """Export candidate data in JSON format (GDPR data portability)"""
        candidate = self.get_candidate_data(candidate_id)
        
        if candidate:
            return json.dumps(candidate, indent=2, default=str)
        
        return None
    
    def get_statistics(self) -> Dict:
        """Get anonymized statistics about candidates"""
        candidates = self._load_candidates()
        
        if not candidates:
            return {"total_candidates": 0}
        
        # Calculate statistics
        tech_stacks = []
        experience_levels = []
        positions = []
        
        for candidate in candidates:
            data = candidate.get('data', {})
            
            if 'tech_stack' in data:
                tech_stacks.extend(data['tech_stack'])
            
            if 'experience' in data:
                experience_levels.append(data['experience'])
            
            if 'position' in data:
                positions.append(data['position'])
        
        # Count occurrences
        from collections import Counter
        
        stats = {
            "total_candidates": len(candidates),
            "popular_technologies": dict(Counter(tech_stacks).most_common(10)),
            "average_experience": sum(experience_levels) / len(experience_levels) if experience_levels else 0,
            "popular_positions": dict(Counter(positions).most_common(5)),
            "last_updated": datetime.now().isoformat()
        }
        
        return stats
