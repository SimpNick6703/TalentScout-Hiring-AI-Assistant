"""
TalentScout Hiring Assistant - Main Streamlit Application
A sophisticated AI-powered chatbot for technical candidate screening and assessment.
"""

import streamlit as st
import json
import re
from datetime import datetime
from typing import Dict, List, Optional
from chatbot import HiringAssistant
from data_handler import DataHandler
from utils import validate_email, validate_phone

# Configure Streamlit page
st.set_page_config(
    page_title="TalentScout - AI Hiring Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS with automatic theme detection
def load_css():
    """Load custom CSS from external file"""
    try:
        with open("static/styles.css", "r", encoding="utf-8") as f:
            css_content = f.read()
        
        st.markdown(f"""
        <style>
        {css_content}
        </style>
        """, unsafe_allow_html=True)
    except FileNotFoundError:
        st.error("⚠️ CSS file not found. Please ensure 'static/styles.css' exists.")
    except Exception as e:
        st.error(f"⚠️ Error loading CSS: {e}")

def initialize_session_state():
    """Initialize session state variables"""
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = HiringAssistant()
    
    if 'data_handler' not in st.session_state:
        st.session_state.data_handler = DataHandler()
    
    if 'conversation_started' not in st.session_state:
        st.session_state.conversation_started = False
    
    if 'conversation_ended' not in st.session_state:
        st.session_state.conversation_ended = False
    
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 'greeting'
    
    if 'candidate_data' not in st.session_state:
        st.session_state.candidate_data = {}
    
    if 'technical_questions' not in st.session_state:
        st.session_state.technical_questions = []
    
    if 'current_question_index' not in st.session_state:
        st.session_state.current_question_index = 0

def render_header():
    """Render the main application header"""
    st.markdown("""
    <div class="main-header">
        <h1>🤖 TalentScout AI</h1>
        <p>Intelligent Hiring Assistant for Technology Placements</p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Render the sidebar with progress and information"""
    with st.sidebar:
        st.markdown("### 📊 Interview Progress")
        
        # Get current phase info from chatbot
        if hasattr(st.session_state, 'chatbot'):
            current_phase = st.session_state.chatbot.interview_phases[st.session_state.chatbot.current_phase_index]
            phase_index = st.session_state.chatbot.current_phase_index
            total_phases = len(st.session_state.chatbot.interview_phases)
            
            # Define progress steps based on actual interview phases
            progress_steps = [
                ("🎯 Greeting", phase_index > 0),
                ("📋 Information Gathering", phase_index > 1), 
                ("🔧 Technical Assessment", phase_index > 2),
                ("💼 Experience Discussion", phase_index > 3),
                ("🚀 Project Deep Dive", phase_index > 4),
                ("🤝 Cultural Fit", phase_index > 5),
                ("❓ Your Questions", phase_index > 6),
                ("✅ Next Steps", phase_index > 7)
            ]
            
            for step_name, completed in progress_steps:
                status = "✅" if completed else ("🔄" if step_name.lower().replace("🎯 ", "").replace("📋 ", "").replace("🔧 ", "").replace("💼 ", "").replace("🚀 ", "").replace("🤝 ", "").replace("❓ ", "").replace("✅ ", "") == current_phase.replace("_", " ") else "⏳")
                st.markdown(f"{status} {step_name}")
            
            # Show current phase info
            st.markdown(f"**Current Phase:** {current_phase.replace('_', ' ').title()}")
            st.markdown(f"**Progress:** {phase_index + 1}/{total_phases}")
        else:
            st.markdown("⏳ Starting interview...")
        
        st.markdown("---")
        
        # Display candidate information if available
        if st.session_state.candidate_data:
            st.markdown("### 👤 Candidate Info")
            candidate = st.session_state.candidate_data
            
            # Required fields tracking
            required_fields = ['name', 'email', 'phone', 'experience', 'position', 'location', 'tech_stack']
            collected_fields = [field for field in required_fields if field in candidate and candidate[field]]
            missing_fields = [field for field in required_fields if field not in candidate or not candidate[field]]
            
            st.markdown(f"**Collected:** {len(collected_fields)}/{len(required_fields)} fields")
            
            if collected_fields:
                st.markdown("**✅ Information Collected:**")
                if 'name' in candidate:
                    st.markdown(f"📝 **Name:** {candidate['name']}")
                if 'email' in candidate:
                    st.markdown(f"📧 **Email:** {candidate['email']}")
                if 'phone' in candidate:
                    st.markdown(f"📞 **Phone:** {candidate['phone']}")
                if 'experience' in candidate:
                    st.markdown(f"⏰ **Experience:** {candidate['experience']} years")
                if 'position' in candidate:
                    st.markdown(f"💼 **Position:** {candidate['position']}")
                if 'location' in candidate:
                    st.markdown(f"📍 **Location:** {candidate['location']}")
                if 'tech_stack' in candidate:
                    st.markdown(f"⚙️ **Tech Stack:** {candidate['tech_stack']}")
            
            if missing_fields:
                st.markdown("**⏳ Still Need:**")
                for field in missing_fields:
                    field_display = field.replace('_', ' ').title()
                    st.markdown(f"• {field_display}")
        else:
            st.markdown("### 👤 Candidate Info")
            st.markdown("*No information collected yet*")
        
        st.markdown("---")
          # Control buttons
        if st.button("🔄 Reset Interview", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
            
        if st.button("💾 Export Data", use_container_width=True):
            if st.session_state.candidate_data:
                # Use the comprehensive interview export
                try:
                    interview_summary = st.session_state.chatbot.get_conversation_summary()
                    
                    # Create comprehensive export data
                    export_data = {
                        'export_metadata': {
                            'exported_at': datetime.now().isoformat(),
                            'export_version': '2.0',
                            'interview_system': 'TalentScout AI Hiring Assistant'
                        },
                        'candidate_information': st.session_state.candidate_data,
                        'interview_summary': {
                            'current_phase': interview_summary.get('current_phase', 'Unknown'),
                            'phase_index': interview_summary.get('phase_index', 0),
                            'completion_percentage': interview_summary.get('completion_percentage', 0),
                            'interview_completed': interview_summary.get('interview_completed', False),
                            'missing_information': interview_summary.get('missing_information', [])
                        },
                        'full_conversation': getattr(st.session_state.chatbot, 'conversation_history', []),
                        'interview_analysis': {
                            'information_completeness': interview_summary.get('completion_percentage', 0),
                            'engagement_level': min(100, len(getattr(st.session_state.chatbot, 'conversation_history', [])) * 3),
                            'total_messages': len(getattr(st.session_state.chatbot, 'conversation_history', [])),
                            'estimated_duration': f"{len(getattr(st.session_state.chatbot, 'conversation_history', [])) * 0.5:.1f} minutes",
                            'phases_covered': interview_summary.get('phase_index', 0) + 1
                        },
                        'conversation_transcript': [
                            {
                                'speaker': 'Assistant' if msg['role'] == 'assistant' else 'Candidate',
                                'message': msg['content'],
                                'timestamp': msg.get('timestamp', 'Unknown')
                            }
                            for msg in getattr(st.session_state.chatbot, 'conversation_history', [])
                        ]
                    }
                    
                    data_json = json.dumps(export_data, indent=2, ensure_ascii=False)
                    
                    st.download_button(
                        label="📥 Download Complete Interview Data",
                        data=data_json,
                        file_name=f"interview_{st.session_state.candidate_data.get('name', 'candidate').replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
                    
                    st.success("✅ Interview data prepared for download!")
                    
                except Exception as e:
                    st.error(f"Export failed: {e}")
                    # Fallback to basic export
                    data_json = json.dumps(st.session_state.candidate_data, indent=2)
                    st.download_button(
                        label="📥 Download Basic Data",
                        data=data_json,
                        file_name=f"candidate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
            else:
                st.warning("No candidate data to export yet.")

def render_chat_interface():
    """Render the main chat interface using Streamlit's chat elements"""
    # Display conversation history using st.chat_message
    if hasattr(st.session_state.chatbot, 'conversation_history'):
        for message in st.session_state.chatbot.conversation_history:
            if message['role'] == 'user':
                with st.chat_message("user"):
                    st.markdown(message["content"])
            elif message['role'] == 'assistant':
                with st.chat_message("assistant"):
                    st.markdown(message["content"])

def handle_user_input():
    """Handle user input and generate bot responses with streaming"""
    user_input = st.chat_input("Type your message here...", key="user_input")
    
    if user_input and not st.session_state.conversation_ended:
        # Display user message immediately
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Display streaming assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                # Process user input through the chatbot with streaming
                for chunk in st.session_state.chatbot.process_message_stream(user_input):
                    full_response += chunk
                    # Update display with current response + typing indicator
                    message_placeholder.markdown(full_response + "▌")
                
                # Final update without cursor
                message_placeholder.markdown(full_response)
                
            except Exception as e:
                # Fallback to non-streaming if streaming fails
                st.warning(f"Streaming mode unavailable, using standard mode.")
                response = st.session_state.chatbot.process_message(user_input)
                message_placeholder.markdown(response)
                full_response = response
        
        # Update session state based on chatbot response
        if hasattr(st.session_state.chatbot, 'current_step'):
            st.session_state.current_step = st.session_state.chatbot.current_step
        
        if hasattr(st.session_state.chatbot, 'candidate_data'):
            st.session_state.candidate_data.update(st.session_state.chatbot.candidate_data)
        
        # Check if conversation should end
        if any(keyword in user_input.lower() for keyword in ['bye', 'goodbye', 'exit', 'quit', 'end']):
            st.session_state.conversation_ended = True
            st.session_state.data_handler.save_candidate_data(st.session_state.candidate_data)
        
        st.rerun()

def handle_user_input_stream():
    """Alternative streaming handler using st.write_stream"""
    user_input = st.chat_input("Type your message here...", key="user_input_stream")
    
    if user_input and not st.session_state.conversation_ended:
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Display streaming assistant response
        with st.chat_message("assistant"):
            try:
                # Create a simple text generator for st.write_stream
                def simple_stream():
                    for chunk in st.session_state.chatbot.process_message_stream(user_input):
                        yield chunk
                
                # Use st.write_stream for visible token streaming
                full_response = st.write_stream(simple_stream())
                
            except Exception as e:
                # Fallback to non-streaming
                st.error(f"Streaming failed: {e}")
                response = st.session_state.chatbot.process_message(user_input)
                st.markdown(response)
                full_response = response
        
        # Update session state
        if hasattr(st.session_state.chatbot, 'current_step'):
            st.session_state.current_step = st.session_state.chatbot.current_step
        
        if hasattr(st.session_state.chatbot, 'candidate_data'):
            st.session_state.candidate_data.update(st.session_state.chatbot.candidate_data)
        
        # Check if conversation should end
        if any(keyword in user_input.lower() for keyword in ['bye', 'goodbye', 'exit', 'quit', 'end']):
            st.session_state.conversation_ended = True
            st.session_state.data_handler.save_candidate_data(st.session_state.candidate_data)

def render_info_cards():
    """Render informational cards with consistent spacing"""
    col1, col2, col3 = st.columns(3, gap="medium")
    
    with col1:
        st.markdown("""
        <div class="info-card">
            <h3>🎯 Purpose</h3>
            <p>Our AI assistant guides you through initial screening, gathering information and assessing technical skills.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="info-card">
            <h3>⏱️ Duration</h3>
            <p>Interview typically takes 10-15 minutes, depending on your responses and background.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="info-card">
            <h3>🔒 Privacy</h3>
            <p>Your information is handled securely in compliance with data privacy standards.</p>
        </div>
        """, unsafe_allow_html=True)

def main():
    """Main application function"""
    # Load CSS and initialize
    load_css()
    initialize_session_state()
    
    # Render header
    render_header()
    
    # Create main layout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Show info cards if conversation hasn't started
        if not st.session_state.conversation_started:
            render_info_cards()
            
            if st.button("🚀 Start Interview", use_container_width=True, type="primary"):
                st.session_state.conversation_started = True
                # Initialize conversation with greeting
                greeting = st.session_state.chatbot.get_greeting()
                st.rerun()
        else:
            # Render chat interface
            render_chat_interface()
            
            # Handle user input with streaming (using more reliable method)
            handle_user_input()
            
            # Show completion message if interview is done
            if st.session_state.conversation_ended:
                st.success("🎉 Interview completed! Thank you for your time.")
                st.info("Our team will review your responses and get back to you soon.")
    
    with col2:
        render_sidebar()

if __name__ == "__main__":
    main()
