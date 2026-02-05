import os
from dotenv import load_dotenv
import streamlit as st
import time
from textblob import TextBlob
from src.llm_engine import LLMEngine
from src.data_handler import save_candidate_info

load_dotenv()

# Page Config
st.set_page_config(
    page_title="TalentScout Hiring Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
def load_css():
    with open("assets/style.css") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

load_css()

# Session State Initialization
if 'page' not in st.session_state:
    st.session_state.page = 'landing'
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'candidate_data' not in st.session_state:
    st.session_state.candidate_data = {}
if 'llm_engine' not in st.session_state:
    st.session_state.llm_engine = None
if 'current_q_index' not in st.session_state:
    st.session_state.current_q_index = 0

# Sidebar Configuration
with st.sidebar:
    st.title("⚙️ Configuration")
    
    # Auto-load key from environment
    default_api_key = os.getenv("OPENAI_API_KEY", "")
    
    api_key_input = st.text_input("OpenAI API Key (Optional)", value=default_api_key, type="password", help="Leave empty to use Demo Mode (Simulated AI).")
    
    if api_key_input != st.session_state.get('api_key', ''):
        st.session_state.api_key = api_key_input
        # Re-init engine if key changes
        st.session_state.llm_engine = LLMEngine(api_key=api_key_input)
    
    if st.session_state.llm_engine is None:
        st.session_state.llm_engine = LLMEngine(api_key=api_key_input if 'api_key' in st.session_state else None)
        
    st.info("💡 **Tip**: In Demo Mode, the AI mimics responses without external API calls.")
    
    st.markdown("### 🌐 Localization")
    language = st.selectbox("Preferred Language", ["English", "Spanish", "French", "German", "Hindi"])

    st.markdown("---")
    st.caption("TalentScout © 2026")
    
    if st.session_state.page == 'chat':
        st.markdown("### 📊 Interview Analytics")
        if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
            last_user_msg = st.session_state.messages[-1]["content"]
            blob = TextBlob(last_user_msg)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            st.write("Candidate Sentiment:")
            st.progress((polarity + 1) / 2) # Normalize -1..1 to 0..1
            
            if polarity > 0.5:
                st.caption("State: 🤩 Enthusiastic")
            elif polarity > 0:
                st.caption("State: 🙂 Positive")
            elif polarity < -0.5:
                st.caption("State: 😤 Frustrated")
            elif polarity < 0:
                st.caption("State: 😟 Concerned")
            else:
                st.caption("State: 😐 Neutral")

def main():
    # --- LANDING PAGE ---
    if st.session_state.page == 'landing':
        st.title("Welcome to TalentScout 🚀")
        st.markdown("""
        ### Your AI-Powered Recruitment Companion
        
        Hello! I am the TalentScout Hiring Assistant. My goal is to get to know you better and assess your technical fit for our open roles.
        
        **Process:**
        1. **Profile Setup**: Tell us about yourself.
        2. **Tech Stack**: Define your expertise.
        3. **Technical Screening**: specific questions tailored to *your* skills.
        
        Ready to begin?
        """)
        
        if st.button("Start Interview", key="start_btn"):
            st.session_state.page = 'info_form'
            st.rerun()

    # --- INFO GATHERING ---
    elif st.session_state.page == 'info_form':
        st.title("📝 Candidate Profile")
        
        with st.form("candidate_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Full Name")
                email = st.text_input("Email Address")
                phone = st.text_input("Phone Number")
            with col2:
                yoe = st.number_input("Years of Experience", min_value=0, max_value=50, step=1)
                position = st.text_input("Desired Position(s)")
                location = st.text_input("Current Location")
            
            st.markdown("### 💻 Technology Stack")
            tech_stack = st.text_area("List your Programming Languages, Frameworks, and Tools", 
                                     placeholder="e.g., Python, Django, React, AWS, Docker...")
            
            submitted = st.form_submit_button("Submit & Generate Questions")
            
            if submitted:
                if not name or not email or not tech_stack:
                    st.error("Please fill in the required fields (Name, Email, Tech Stack).")
                else:
                    # Save Data
                    data = {
                        "name": name,
                        "email": email,
                        "phone": phone,
                        "experience": yoe,
                        "position": position,
                        "location": location,
                        "tech_stack": tech_stack
                    }
                    st.session_state.candidate_data = data
                    
                    # Generate Questions
                    with st.spinner("Analyzing your tech stack and generating questions..."):
                        # Get questions from LLM (now returns a LIST)
                        questions_list = st.session_state.llm_engine.generate_questions(tech_stack, language=language)
                        st.session_state.questions = questions_list
                        st.session_state.current_q_index = 0
                        
                        # Add initial bot message with FIRST question
                        first_q = questions_list[0] if questions_list else "Tell me about your experience."
                        
                        st.session_state.messages = [
                            {"role": "assistant", "content": f"Hi {name}! Thanks for sharing your details. Based on your experience with **{tech_stack}**, I'd like to ask you a few questions.\n\nLet's start:\n\n**1. {first_q}**"}
                        ]
                        
                        save_candidate_info(data) # Initial save
                        
                    st.session_state.page = 'chat'
                    st.rerun()

    # --- CHAT INTERFACE ---
    elif st.session_state.page == 'chat':
        st.title("💬 Technical Screening")
        
        # Display Chat History
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f'<div class="user-message">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="bot-message">🤖 <b>Assistant</b><br>{msg["content"]}</div>', unsafe_allow_html=True)
        
        # Chat Input Logic
        if st.session_state.current_q_index < len(st.session_state.questions):
            if prompt := st.chat_input("Type your answer here..."):
                # Add user message
                st.session_state.messages.append({"role": "user", "content": prompt})
                
                # Check for exit keywords
                if any(keyword in prompt.lower() for keyword in ["quit", "exit", "bye", "end conversation"]):
                    st.session_state.last_message = "Thank you for your time! We have recorded your responses. Our team will be in touch soon."
                    st.session_state.page = 'end'
                    st.rerun()
                
                # Save answer (logic to map answer to question could be added here)
                
                # Move to next question
                st.session_state.current_q_index += 1
                next_q = None
                if st.session_state.current_q_index < len(st.session_state.questions):
                    next_q = st.session_state.questions[st.session_state.current_q_index]
                    # Format next question
                    api_next_q = f"**{st.session_state.current_q_index + 1}. {next_q}**"
                else:
                    api_next_q = None

                # Generate response
                with st.spinner("Thinking..."):
                    response = st.session_state.llm_engine.chat_response(
                        st.session_state.messages, 
                        prompt, 
                        language=language,
                        next_question=api_next_q
                    )
                    st.session_state.messages.append({"role": "assistant", "content": response})
                
                st.rerun()
                
            if st.button("End Interview Early", type="secondary"):
                st.session_state.page = 'end'
                st.rerun()

        else:
            # Interview Complete
            st.info("✅ You have answered all the technical questions.")
            if st.button("Submit Interview & Finish", type="primary", use_container_width=True):
                st.session_state.page = 'end'
                st.rerun()

    # --- END SCREEN ---
    elif st.session_state.page == 'end':
        st.balloons()
        st.title("Thank You! 🎉")
        st.success("Your interview has been successfully recorded.")
        
        st.markdown(f"""
        ### Next Steps
        Dear **{st.session_state.candidate_data.get('name', 'Candidate')}**,
        
        We appreciate the time you took to complete this screening. Your responses regarding **{st.session_state.candidate_data.get('tech_stack', 'your tech stack')}** have been saved.
        
        Our recruitment team at **TalentScout** will review your profile and get back to you at **{st.session_state.candidate_data.get('email', 'your email')}** within 48 hours.
        """)
        
        if st.button("Start New Interview"):
            # Clear all session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

if __name__ == "__main__":
    main()
