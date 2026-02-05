# TalentScout Hiring Assistant 🤖

## 📋 Project Overview
TalentScout is an intelligent Hiring Assistant chatbot designed to streamline the specific initial screening process for technology candidates. It leverages Large Language Models (LLMs) to gather candidate information and generate tailored technical interview questions based on the candidate's declared tech stack.

## 🚀 Features
- **Smart Information Gathering**: Collects candidate details (Name, Contact, Experience, etc.) via an intuitive interface.
- **Dynamic Question Generation**: specific AI-generated technical questions based on the user's tech stack (e.g., Python, React, AWS).
- **Context-Aware Chat**: Maintains conversation context for a seamless experience.
- **Simulated Backend**: Securely stores candidate data locally for review.
- **Premium UI**: Polished, modern interface using Streamlit with custom CSS.

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd TalentScout-HiringAssistant
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   python -m textblob.download_corpora
   ```

3. **Set up Environment** (Optional for Real AI):
   - Create a `.env` file or enter your OpenAI API Key in the application sidebar.
   - If no key is provided, the app runs in **Demo Mode** with simulated responses.

4. **Run the Application**:
   ```bash
   streamlit run app.py
   ```

## 🏗️ Technical Details
- **Frontend**: Streamlit (Python)
- **AI Engine**: OpenAI GPT models (configurable).
- **Styling**: Custom CSS injection for a recruiting agency brand feel.
- **Data Storage**: Local JSON storage (simulating a database).

## 🧠 Prompt Design
The application uses a two-stage prompting strategy:
1.  **Contextual Role-Play**: The LLM is instructed to act as a Senior Technical Recruiter.
2.  **Few-Shot Construction**: Questions are generated using structure constraints (Topic, Difficulty, Question).

## ⚠️ Challenges & Solutions
- **Challenge**: ensuring the LLM doesn't hallucinate non-existent technologies.
  - *Solution*: Added a validation step in the prompt to stick strictly to the user's provided stack.
- **Challenge**: Managing session state in Streamlit during the chat flow.
  - *Solution*: Implemented a robust `session_state` management system to preserve chat history across re-runs.

---
*Built for the AI/ML Intern Assignment.*
