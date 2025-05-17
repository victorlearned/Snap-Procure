import streamlit as st
from dotenv import load_dotenv
import os
import json
from datetime import datetime
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.absolute()))

# Import the SnapProcure crew
from src.snap_procure.crew import SnapProcure

# Set page config
st.set_page_config(
    page_title="SnapProcure",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern look
st.markdown("""
    <style>
    .main {
        max-width: 1200px;
        padding: 2rem;
    }
    .header {
        padding: 2rem 0;
        border-bottom: 1px solid #eaeaea;
        margin-bottom: 2rem;
    }
    .title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a1a1a;
        margin: 0;
    }
    .subtitle {
        color: #666;
        margin: 0.5rem 0 0 0;
    }
    .card {
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 0.5rem 1.5rem;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 1rem;
        margin: 0.5rem 0;
        cursor: pointer;
        border-radius: 4px;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .stTextArea>div>div>textarea {
        min-height: 120px;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'instructions' not in st.session_state:
    st.session_state.instructions = ""
if 'llm_id' not in st.session_state:
    st.session_state.llm_id = "gpt-4-turbo"
if 'show_thinking_process' not in st.session_state:
    st.session_state.show_thinking_process = True
if 'responses' not in st.session_state:
    st.session_state.responses = []

# Load environment variables
load_dotenv()

def render_sidebar():
    st.sidebar.title("SnapProcure Settings")
    
    with st.sidebar.expander("⚙️ Configuration", expanded=True):
        model = st.selectbox(
            "Model",
            ["gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"],
            index=0,
            help="Select the model to use"
        )
        if model != st.session_state.llm_id:
            st.session_state.llm_id = model
    
    with st.sidebar.expander("🔍 Display Options", expanded=True):
        show_thinking = st.checkbox(
            "Show thinking process",
            value=st.session_state.show_thinking_process,
            help="Show the agent's thinking process"
        )
        if show_thinking != st.session_state.show_thinking_process:
            st.session_state.show_thinking_process = show_thinking

def render_header():
    st.markdown("""
    <div class="header">
        <h1 class="title">SnapProcure AI</h1>
        <p class="subtitle">Streamline your procurement process with AI-powered assistance</p>
    </div>
    """, unsafe_allow_html=True)

def render_input_form():
    with st.container():
        st.markdown("### 📝 Enter Your Procurement Request")
        
        # Wrap in a form
        with st.form(key="procurement_form"):
            instructions = st.text_area(
                label="Your request",
                value=st.session_state.instructions,
                placeholder="E.g., I need to order 10 high-performance laptops for our new engineering team...",
                label_visibility="visible"
            )
            
            # Store the instructions in the session state
            if instructions != st.session_state.instructions:
                st.session_state.instructions = instructions
            
            # Process button
            if st.form_submit_button("🚀 Process Request", use_container_width=True):
                if not st.session_state.instructions:
                    st.error("Please enter your procurement request.")
                else:
                    st.session_state.processing = True

def process_request(user_input):
    """Process user input using the SnapProcure crew."""
    try:
        # Initialize the crew
        bot = SnapProcure()
        crew = bot.crew()
        
        # Process the request
        response = crew.kickoff(inputs={"user_request": user_input})
        
        # Format the response for display
        response_data = {
            "summary": response,
            "recommendations": [],
            "next_steps": [
                "Review the information above",
                "Ask follow-up questions if needed"
            ]
        }
        
        return response_data
    except Exception as e:
        error_msg = str(e)
        if "No API key provided" in error_msg or "Incorrect API key" in error_msg:
            st.sidebar.error("❌ Invalid or missing OpenAI API key. Please check your .env file.")
        else:
            st.error(f"Error processing request: {error_msg}")
        return None

def render_response():
    if hasattr(st.session_state, 'processing') and st.session_state.processing:
        with st.spinner("🧠 Analyzing your request... This may take a moment."):
            # Process the request using the crew
            response_data = process_request(st.session_state.instructions)
            
            if response_data:
                # Store the response
                response_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "request": st.session_state.instructions,
                    "response": response_data
                }
                st.session_state.responses.append(response_entry)
            
            # Reset processing state
            st.session_state.processing = False
            st.session_state.instructions = ""  # Clear the input
            st.rerun()
    
    # Display responses in reverse order (newest first)
    for i, response in enumerate(reversed(st.session_state.responses)):
        with st.container():
            st.markdown(f"### 📋 Request {len(st.session_state.responses) - i}")
            st.info(f"**Your request:** {response['request']}")
            
            st.markdown("#### 💡 Response")
            st.write(response['response']['summary'])
            
            if response['response']['recommendations']:
                st.markdown("#### 🖥️ Recommended Options")
                for rec in response['response']['recommendations']:
                    with st.expander(f"{rec['model']} - {rec['price']}" if 'model' in rec else "View details"):
                        for key, value in rec.items():
                            if key != 'model' and key != 'price':
                                st.write(f"**{key.replace('_', ' ').title()}:** {value}")
            
            if response['response']['next_steps']:
                st.markdown("#### ➡️ Next Steps")
                for step in response['response']['next_steps']:
                    st.markdown(f"- {step}")
            
            st.markdown("---")

def main():
    render_sidebar()
    render_header()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        render_input_form()
        
        if hasattr(st.session_state, 'processing') and st.session_state.processing:
            render_response()
        elif st.session_state.responses:
            render_response()
    
    with col2:
        st.markdown("### ℹ️ About")
        st.markdown("""
        **SnapProcure AI** helps you streamline your procurement process by:
        - Analyzing your requirements
        - Finding the best options
        - Providing vendor recommendations
        - Assisting with the purchase process
        
        Simply describe what you need, and let AI handle the rest!
        """)
        
        st.markdown("### 📊 Recent Activity")
        if not st.session_state.responses:
            st.info("No recent activity. Submit a request to get started!")
        else:
            for i, response in enumerate(st.session_state.responses):
                st.caption(f"{i+1}. {response['request'][:50]}...")

if __name__ == "__main__":
    main()