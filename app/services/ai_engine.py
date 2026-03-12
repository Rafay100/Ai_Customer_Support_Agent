import os
from typing import Optional, Dict, List
from dotenv import load_dotenv
from app.core.knowledge_base import FAQS, ESCALATION_KEYWORDS, PRICING_KEYWORDS

load_dotenv()

class AIEngine:
    """
    Simple AI Engine for FAQ matching and response generation
    Uses keyword matching + optional LLM integration
    """
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.use_llm = bool(self.openai_api_key and self.openai_api_key != "your_openai_api_key_here")
    
    def find_best_faq(self, query: str) -> Optional[Dict]:
        """Find the best matching FAQ for a query"""
        query_lower = query.lower()
        
        best_match = None
        best_score = 0
        
        for faq in FAQS:
            score = 0
            # Check keyword matches
            for keyword in faq["keywords"]:
                if keyword.lower() in query_lower:
                    score += 1
            
            # Also check if FAQ question words appear in query
            question_words = faq["question"].lower().split()
            for word in question_words:
                if len(word) > 3 and word in query_lower:
                    score += 0.5
            
            if score > best_score and score > 0:
                best_score = score
                best_match = faq
        
        return best_match if best_score >= 1 else None
    
    def should_escalate(self, message: str) -> bool:
        """Check if message should be escalated to human"""
        message_lower = message.lower()
        
        # Check escalation keywords
        for keyword in ESCALATION_KEYWORDS:
            if keyword.lower() in message_lower:
                return True
        
        # Check pricing keywords (often need human)
        for keyword in PRICING_KEYWORDS:
            if keyword.lower() in message_lower:
                return True
        
        # Check for urgency indicators
        urgency_indicators = ["urgent", "asap", "immediately", "right now", "emergency"]
        for indicator in urgency_indicators:
            if indicator in message_lower:
                return True
        
        return False
    
    def generate_response(self, query: str, channel: str = "web_form") -> Dict:
        """
        Generate appropriate response based on query and channel
        Returns: {response: str, should_escalate: bool, confidence: str}
        """
        # Check for escalation first
        if self.should_escalate(query):
            return {
                "response": self._get_escalation_message(channel),
                "should_escalate": True,
                "confidence": "high"
            }
        
        # Try to find matching FAQ
        faq_match = self.find_best_faq(query)
        
        if faq_match:
            response = self._format_response(faq_match["answer"], channel)
            return {
                "response": response,
                "should_escalate": False,
                "confidence": "high"
            }
        
        # No good match found
        return {
            "response": self._get_fallback_message(channel),
            "should_escalate": True,
            "confidence": "low"
        }
    
    def _format_response(self, answer: str, channel: str) -> str:
        """Format response based on channel"""
        if channel == "whatsapp":
            # Keep it short for WhatsApp
            if len(answer) > 160:
                return answer[:157] + "..."
            return answer
        elif channel == "email":
            # More formal for email
            return f"Thank you for contacting us.\n\n{answer}\n\nBest regards,\nCustomer Support Team"
        else:
            # Default for web form
            return answer
    
    def _get_escalation_message(self, channel: str) -> str:
        """Get message when escalating to human"""
        if channel == "whatsapp":
            return "I understand this needs personal attention. Let me connect you with a support agent. Please wait."
        elif channel == "email":
            return "Thank you for reaching out. Your query requires special attention from our team. A support agent will respond within 24 hours.\n\nTicket ID will be sent shortly."
        else:
            return "This query needs human assistance. A support agent will respond shortly. Your ticket has been created."
    
    def _get_fallback_message(self, channel: str) -> str:
        """Get fallback message when no FAQ matches"""
        if channel == "whatsapp":
            return "I'm not sure I understand. Let me get a human agent to help you better. Please wait."
        elif channel == "email":
            return "Thank you for your message. To serve you better, I'm forwarding this to our support team. Expect a response within 24 hours."
        else:
            return "I couldn't find an answer to your question. Let me connect you with a human agent who can help better."


# Simple test
if __name__ == "__main__":
    engine = AIEngine()
    
    test_queries = [
        "How long does shipping take?",
        "I want to return my product",
        "I'm very angry about the delay!",
        "Can I get a discount?",
        "Where is my order?"
    ]
    
    print("Testing AI Engine\n" + "="*50)
    for query in test_queries:
        result = engine.generate_response(query, "web_form")
        print(f"\nQ: {query}")
        print(f"A: {result['response']}")
        print(f"Escalate: {result['should_escalate']}, Confidence: {result['confidence']}")
