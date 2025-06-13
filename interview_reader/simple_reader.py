"""
Simple Interview Conversation Reader - A minimal tool to read interview conversations
"""

import os
import json
import sys
from flask import Flask, render_template, request, flash, redirect, url_for
from datetime import datetime

app = Flask(__name__)

DEFAULT_EXPORTS_DIR = os.path.abspath(os.path.dirname(__file__))

def format_timestamp(timestamp_str):
    """Format ISO timestamp to readable format"""
    try:
        dt = datetime.fromisoformat(timestamp_str)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return timestamp_str or ""

def load_interview(file_path):
    """Load interview data from JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading interview: {str(e)}")
        return None

def find_interview_files(directory=DEFAULT_EXPORTS_DIR):
    """Find all interview JSON files in the directory"""
    interview_files = []
    
    for filename in os.listdir(directory):
        if filename.lower().startswith("interview_") and filename.lower().endswith(".json"):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                interview_files.append({
                    "filename": filename,
                    "path": file_path,
                    "modified": datetime.fromtimestamp(os.path.getmtime(file_path))
                })
    
    interview_files.sort(key=lambda x: x["modified"], reverse=True)
    return interview_files

def get_conversation(interview_data):
    """Extract conversation from interview data, handling different formats"""
    if "full_conversation" in interview_data:
        return interview_data["full_conversation"]
    elif "conversation_history" in interview_data:
        return interview_data["conversation_history"]
    elif "conversation_transcript" in interview_data:
        transcript = interview_data["conversation_transcript"]
        conversation = []
        for message in transcript:
            role = message["speaker"].lower()
            if role == "candidate":
                role = "user"
            elif role == "assistant":
                role = "assistant"
            
            conversation.append({
                "role": role,
                "content": message["message"],
                "timestamp": message["timestamp"]
            })
        return conversation
    
    return []

@app.route('/')
def index():
    """Home page - list all interview files"""
    interview_files = find_interview_files()
    return render_template('index.html', interview_files=interview_files)

@app.route('/conversation/<path:filename>')
def view_conversation(filename):
    """View a specific interview conversation"""
    file_path = os.path.join(DEFAULT_EXPORTS_DIR, filename)
    interview_data = load_interview(file_path)
    
    if interview_data:
        candidate_name = "Unknown"
        if "candidate_information" in interview_data and "name" in interview_data["candidate_information"]:
            candidate_name = interview_data["candidate_information"]["name"]
        
        interview_date = ""
        if "export_metadata" in interview_data and "exported_at" in interview_data["export_metadata"]:
            interview_date = format_timestamp(interview_data["export_metadata"]["exported_at"])
        
        conversation = get_conversation(interview_data)
        
        for message in conversation:
            if "timestamp" in message:
                message["formatted_time"] = format_timestamp(message["timestamp"])
        
        return render_template('conversation.html', 
                              conversation=conversation,
                              candidate_name=candidate_name,
                              interview_date=interview_date,
                              filename=filename)
    else:
        flash("Error loading interview file", "error")
        return redirect(url_for('index'))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        exports_dir = sys.argv[1]
        if os.path.isdir(exports_dir):
            DEFAULT_EXPORTS_DIR = os.path.abspath(exports_dir)
    
    print(f"Looking for interview files in: {DEFAULT_EXPORTS_DIR}")
    app.run(debug=True, port=5001)
