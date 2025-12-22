import os
from typing import List, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
import requests

class ChatbotEngine:
    """Healthcare Chatbot Engine using LangChain and Gemini API"""
    
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        # Initialize Gemini model with LangChain
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=self.gemini_api_key,
            temperature=0.7,
            max_tokens=1000
        )
        
        # Service URLs
        self.medical_service_url = os.getenv("MEDICAL_SERVICE_URL", "http://localhost:8002")
        self.scheduling_service_url = os.getenv("SCHEDULING_SERVICE_URL", "http://localhost:8003")
        
        # System prompt
        self.system_prompt = """You are a helpful healthcare assistant for a medical platform. Your role is to:

1. Answer general health questions in a clear, empathetic manner
2. Help users find appropriate doctors based on their symptoms
3. Guide users through appointment booking process
4. Explain medical terms in simple language
5. Provide hospital information

IMPORTANT GUIDELINES:
- Always be empathetic and professional
- For serious symptoms, advise seeing a doctor immediately
- Never diagnose conditions - only suggest which specialist to consult
- You're an AI assistant, not a licensed medical professional
- If unsure, acknowledge limitations

When users describe symptoms, suggest appropriate specializations:
- Chest pain, heart issues → Cardiologist
- Digestive problems → Gastroenterologist
- Skin conditions → Dermatologist
- Joint/bone pain → Orthopedic Surgeon
- Mental health → Psychiatrist
- Children's health → Pediatrician
- General illness → General Practitioner
- Eye problems → Ophthalmologist
- Dental issues → Dentist

Respond naturally and conversationally."""

    def get_response(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        user_context: Dict
    ) -> str:
        """Generate chatbot response using Gemini"""
        
        # Check for specific actions first
        action_response = self._check_for_actions(user_message, user_context)
        if action_response:
            return action_response
        
        # Build conversation messages
        messages = [("system", self.system_prompt)]
        
        # Add history (excluding last message which is current)
        for msg in conversation_history[:-1]:
            if msg["role"] == "user":
                messages.append(("human", msg["content"]))
            else:
                messages.append(("assistant", msg["content"]))
        
        # Add current message
        messages.append(("human", user_message))
        
        # Generate response
        try:
            prompt = ChatPromptTemplate.from_messages(messages)
            chain = prompt | self.llm
            response = chain.invoke({})
            return response.content
        except Exception as e:
            return f"I apologize, but I'm having trouble processing your request. Please try again. Error: {str(e)}"
    
    def _check_for_actions(self, message: str, user_context: Dict) -> str:
        """Check if message requires specific actions"""
        message_lower = message.lower()
        
        # Doctor search
        if any(word in message_lower for word in ["find doctor", "need doctor", "which doctor"]):
            return self._help_find_doctor(message)
        
        # Hospital search
        if any(word in message_lower for word in ["hospital", "find hospital"]):
            return self._help_find_hospital(message)
        
        # Appointment queries
        if any(word in message_lower for word in ["my appointment", "upcoming appointment"]):
            return "To check your appointments, please visit the 'My Appointments' section in the app."
        
        # Booking guide
        if any(word in message_lower for word in ["book appointment", "schedule appointment"]):
            return self._guide_booking()
        
        return None
    
    def _help_find_doctor(self, message: str) -> str:
        """Help find appropriate doctor"""
        message_lower = message.lower()
        
        specialization_map = {
            "chest pain": "Cardiologist",
            "heart": "Cardiologist",
            "stomach": "Gastroenterologist",
            "digestive": "Gastroenterologist",
            "skin": "Dermatologist",
            "rash": "Dermatologist",
            "bone": "Orthopedic Surgeon",
            "joint": "Orthopedic Surgeon",
            "mental": "Psychiatrist",
            "anxiety": "Psychiatrist",
            "child": "Pediatrician",
            "eye": "Ophthalmologist",
            "tooth": "Dentist",
            "fever": "General Practitioner",
            "cold": "General Practitioner"
        }
        
        suggested_spec = None
        for symptom, spec in specialization_map.items():
            if symptom in message_lower:
                suggested_spec = spec
                break
        
        if suggested_spec:
            return f"Based on your symptoms, I recommend consulting a {suggested_spec}. You can use the 'Find Doctors' feature to see available specialists."
        
        return "Could you describe your symptoms in more detail? This will help me suggest the right specialist."
    
    def _help_find_hospital(self, message: str) -> str:
        """Help find hospitals"""
        return "I can help you find hospitals. Please use the 'Find Hospitals' feature in the app to see nearby facilities."
    
    def _guide_booking(self) -> str:
        """Guide booking process"""
        return """I'd be happy to help you book an appointment! Here's how:

1. Use the 'Find Doctors' feature to search by specialization
2. Select a doctor to view their profile
3. Choose a convenient date and time
4. Confirm your appointment

Would you like me to help you find a doctor for a specific condition?"""