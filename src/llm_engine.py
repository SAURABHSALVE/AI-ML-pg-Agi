import os
import time
import json
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

class LLMEngine:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.client = None
        self.is_mock = True
        
        if api_key and OpenAI:
            try:
                self.client = OpenAI(api_key=api_key)
                self.is_mock = False
            except Exception as e:
                print(f"Failed to initialize OpenAI client: {e}")
                self.is_mock = True
        else:
            self.is_mock = True

    def generate_questions(self, tech_stack, language="English"):
        """Generates technical interview questions based on the tech stack."""
        if self.is_mock:
            return self._mock_questions(tech_stack)
        
        prompt = f"""
        You are a Senior Technical Recruiter.
        Target Tech Stack: {tech_stack}.
        Target Language: {language}.
        
        Generate 4 distinct, challenging, and relevant technical interview questions.
        Ensure constraints:
        1. Questions must be challenging.
        2. Questions must be written in {language}.
        
        IMPORTANT: Return the output specifically as a raw JSON array of strings. 
        Example: ["Question 1?", "Question 2?", "Question 3?", "Question 4?"]
        Do not include any other text, number prefixes, or markdown formatting.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful hiring assistant. Output JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            content = response.choices[0].message.content.strip()
            # Clean up potential markdown code blocks
            if content.startswith("```json"):
                content = content[7:-3]
            elif content.startswith("```"):
                content = content[3:-3]
                
            return json.loads(content)
        except Exception as e:
            print(f"Error parsing AI questions: {e}")
            return self._mock_questions(tech_stack)

    def chat_response(self, conversation_history, user_input, language="English", next_question=None):
        """Generates a chat response maintaining context."""
        if self.is_mock:
            return self._mock_chat_response(user_input, next_question)

        system_instruction = f"You are TalentScout's Recruiting Assistant. You MUST respond in {language}."
        if next_question:
            system_instruction += f" Acknowledge the candidate's previous answer briefly and constructively in {language}, then cleanely ask the next question: '{next_question}'."
        else:
            system_instruction += f" The interview questions are finished. Thank the candidate in {language} and ask them to click the Submit button."

        messages = [{"role": "system", "content": system_instruction}]
        
        # Add history
        messages.extend(conversation_history[-6:]) # Keep context tight
        messages.append({"role": "user", "content": user_input})
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return "I apologize, but I had a connection hiccup. Let's move on. " + (next_question if next_question else "Please submit your interview.")



    def _mock_questions(self, tech_stack):
        """Fallback mock questions."""
        time.sleep(1.5) 
        return [
            f"Can you explain the core principles of one of the main technologies in your stack: {tech_stack}?",
            "Describe a challenging bug you faced recently and how you resolved it using these tools.",
            "How do you handle state management and data flow in your preferred framework?",
            "What are the security best practices you follow when building APIs?"
        ]

    def _mock_chat_response(self, user_input, next_question=None):
        time.sleep(1)
        ack = "That's a great point. "
        if next_question:
            return ack + f"Now, let's move on.\n\n{next_question}"
        return "Thank you for all your detailed answers! You have completed the technical screening. Please click the Submit button below."
