"""
Advanced AI Agent with OpenAI integration
Supports function calling, conversation memory, and advanced reasoning
"""
import os
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from openai import OpenAI
from app.services.semantic_search import semantic_search
from app.services.routing_rules import RoutingRules, simple_sentiment_analysis
from app.services.kafka_producer import kafka_producer

class AIAgent:
    """
    Production AI Agent with OpenAI integration
    """
    
    def __init__(self):
        self.client = None
        self.enabled = False
        self.model = "gpt-4o-mini"
        
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and openai_key != "your-openai-api-key-here":
            self.client = OpenAI(api_key=openai_key)
            self.enabled = True
            print("[OK] OpenAI AI Agent enabled")
        else:
            print("[WARN] OpenAI AI Agent disabled (using rule-based AI)")
        
        self.routing_rules = RoutingRules()
        self.conversation_memory = ConversationMemory()
    
    def process_message(
        self, 
        message: str, 
        channel: str,
        customer_id: Optional[int] = None,
        ticket_id: Optional[int] = None,
        db_session=None
    ) -> Dict[str, Any]:
        """
        Process customer message with full AI pipeline
        """
        # 1. Get conversation context
        context = self.conversation_memory.get_context(
            customer_id=customer_id,
            ticket_id=ticket_id
        )
        
        # 2. Analyze sentiment
        sentiment = simple_sentiment_analysis(message)
        
        # 3. Check for escalation triggers
        routing_decision = self.routing_rules.get_routing_decision(message, channel)
        
        if routing_decision['should_escalate']:
            return self._create_escalation_response(message, channel, routing_decision)
        
        # 4. Try semantic search (if enabled)
        if semantic_search.enabled and db_session:
            kb_results = semantic_search.search_knowledge_base(
                query=message,
                limit=3,
                db_session=db_session
            )
            if kb_results:
                return self._create_knowledge_response(
                    message, channel, kb_results, context
                )
        
        # 5. Try OpenAI if enabled
        if self.enabled:
            return self._create_openai_response(
                message, channel, context, sentiment
            )
        
        # 6. Fallback to rule-based AI
        return self._create_rule_based_response(message, channel, sentiment)
    
    def _create_openai_response(
        self, 
        message: str, 
        channel: str,
        context: str,
        sentiment: str
    ) -> Dict:
        """Generate response using OpenAI"""
        try:
            system_prompt = self._get_system_prompt(channel, sentiment)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Context: {context}\n\nCustomer: {message}"}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            ai_response = response.choices[0].message.content
            
            return {
                "response": ai_response,
                "should_escalate": False,
                "confidence": "high",
                "ai_model": self.model,
                "source": "openai"
            }
            
        except Exception as e:
            print(f"OpenAI error: {e}")
            return self._create_rule_based_response(message, channel, sentiment)
    
    def _create_knowledge_response(
        self,
        message: str,
        channel: str,
        kb_results: List[Dict],
        context: str
    ) -> Dict:
        """Generate response from knowledge base"""
        best_match = kb_results[0]
        
        response_text = self._format_response(
            best_match['answer'],
            channel
        )
        
        return {
            "response": response_text,
            "should_escalate": False,
            "confidence": "high",
            "source": "knowledge_base",
            "kb_id": best_match['id'],
            "similarity": best_match.get('similarity', 0)
        }
    
    def _create_rule_based_response(
        self,
        message: str,
        channel: str,
        sentiment: str
    ) -> Dict:
        """Fallback rule-based response"""
        from app.core.knowledge_base import FAQS
        
        # Simple keyword matching
        message_lower = message.lower()
        best_match = None
        best_score = 0
        
        for faq in FAQS:
            score = sum(1 for keyword in faq['keywords'] if keyword.lower() in message_lower)
            if score > best_score:
                best_score = score
                best_match = faq
        
        if best_match and best_score > 0:
            return {
                "response": self._format_response(best_match['answer'], channel),
                "should_escalate": False,
                "confidence": "medium",
                "source": "rule_based"
            }
        
        # No match found - escalate
        return {
            "response": self._get_escalation_message(channel),
            "should_escalate": True,
            "confidence": "low",
            "source": "fallback"
        }
    
    def _create_escalation_response(
        self,
        message: str,
        channel: str,
        routing_decision: Dict
    ) -> Dict:
        """Create escalation response"""
        return {
            "response": self._get_escalation_message(channel),
            "should_escalate": True,
            "confidence": "high",
            "reason": routing_decision['reasons'],
            "priority": routing_decision['priority']
        }
    
    def _get_system_prompt(self, channel: str, sentiment: str) -> str:
        """Get system prompt based on channel and sentiment"""
        base_prompt = """You are a helpful AI customer support agent.
        
Guidelines:
- Be friendly, professional, and helpful
- Provide accurate information
- Keep responses concise but complete
- If you don't know something, offer to connect with a human agent
"""
        
        # Channel-specific instructions
        if channel == "whatsapp":
            base_prompt += "\n- Keep responses short (under 160 characters if possible)\n- Use casual, conversational tone\n- Emojis are okay (but use sparingly)"
        elif channel == "email":
            base_prompt += "\n- Use formal, professional tone\n- Provide detailed explanations\n- Include proper greeting and closing"
        else:
            base_prompt += "\n- Use professional but friendly tone\n- Balance brevity with completeness"
        
        # Sentiment-specific instructions
        if sentiment == "negative":
            base_prompt += "\n\nIMPORTANT: Customer seems upset. Be extra empathetic and apologetic. Consider escalating to human agent."
        
        return base_prompt
    
    def _format_response(self, answer: str, channel: str) -> str:
        """Format response for channel"""
        if channel == "whatsapp":
            if len(answer) > 160:
                return answer[:157] + "..."
            return answer
        elif channel == "email":
            return f"Thank you for contacting us.\n\n{answer}\n\nBest regards,\nCustomer Support Team"
        return answer
    
    def _get_escalation_message(self, channel: str) -> str:
        """Get escalation message"""
        if channel == "whatsapp":
            return "I understand this needs personal attention. Let me connect you with a support agent. Please wait. 👤"
        elif channel == "email":
            return "Thank you for reaching out. Your query requires special attention from our team. A support agent will respond within 24 hours."
        return "This query needs human assistance. A support agent will respond shortly."
    
    def update_metrics(self, ticket_id: int, response_data: Dict):
        """Send metrics to Kafka"""
        kafka_producer.send_metrics({
            "ticket_id": ticket_id,
            "ai_handled": not response_data.get('should_escalate'),
            "confidence": response_data.get('confidence'),
            "source": response_data.get('source'),
            "timestamp": datetime.utcnow().isoformat()
        })


class ConversationMemory:
    """
    Manages conversation context and history
    """
    
    def __init__(self):
        self.memory = {}  # In-memory cache (use Redis in production)
        self.max_history = 10
    
    def add_message(
        self,
        customer_id: int,
        ticket_id: int,
        message: str,
        is_from_customer: bool
    ):
        """Add message to conversation memory"""
        key = f"{customer_id}:{ticket_id}"
        
        if key not in self.memory:
            self.memory[key] = []
        
        self.memory[key].append({
            "role": "customer" if is_from_customer else "assistant",
            "content": message,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Keep only last N messages
        if len(self.memory[key]) > self.max_history:
            self.memory[key] = self.memory[key][-self.max_history:]
    
    def get_context(self, customer_id: int = None, ticket_id: int = None) -> str:
        """Get conversation context"""
        if not customer_id or not ticket_id:
            return ""
        
        key = f"{customer_id}:{ticket_id}"
        history = self.memory.get(key, [])
        
        if not history:
            return "No previous conversation history."
        
        context_lines = []
        for msg in history[-5:]:  # Last 5 messages
            role = "Customer" if msg['role'] == 'customer' else "Agent"
            context_lines.append(f"{role}: {msg['content']}")
        
        return "\n".join(context_lines)
    
    def clear_memory(self, customer_id: int, ticket_id: int):
        """Clear conversation memory"""
        key = f"{customer_id}:{ticket_id}"
        if key in self.memory:
            del self.memory[key]


# Global instance
ai_agent = AIAgent()
