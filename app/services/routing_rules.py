"""
Routing Rules Engine
Determines when to escalate to human vs AI handling
Based on content, sentiment, and channel-specific rules
"""
from typing import Dict, List, Tuple
from enum import Enum

class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class RoutingRules:
    """
    Rule-based routing engine for customer messages
    """
    
    # Escalation keywords by category
    ESCALATION_RULES = {
        'complaint': [
            'angry', 'frustrated', 'disappointed', 'unacceptable', 'terrible',
            'worst', 'horrible', 'useless', 'waste', 'complaint', 'sue',
            'legal', 'lawyer', 'court', 'report', 'scam', 'fraud'
        ],
        'urgent': [
            'urgent', 'asap', 'emergency', 'immediately', 'right now',
            'critical', 'deadlines', 'broken', 'not working', 'error'
        ],
        'pricing': [
            'refund', 'chargeback', 'dispute', 'cancel subscription',
            'too expensive', 'overcharged', 'billing error', 'unauthorized'
        ],
        'human_request': [
            'human', 'real person', 'agent', 'manager', 'supervisor',
            'talk to someone', 'speak with', 'customer service'
        ]
    }
    
    # Channel-specific rules
    CHANNEL_RULES = {
        'whatsapp': {
            'max_length': 160,
            'tone': 'casual',
            'emoji_allowed': True,
            'response_time': 'immediate'
        },
        'email': {
            'max_length': 1000,
            'tone': 'formal',
            'emoji_allowed': False,
            'response_time': '24h'
        },
        'web_form': {
            'max_length': 500,
            'tone': 'professional',
            'emoji_allowed': False,
            'response_time': '1h'
        }
    }
    
    def __init__(self):
        self.escalation_threshold = 1  # Number of keyword matches to escalate
    
    def analyze_message(self, message: str) -> Dict:
        """
        Analyze message for routing decision
        Returns: {should_escalate: bool, priority: Priority, reasons: list}
        """
        message_lower = message.lower()
        reasons = []
        priority_score = 0
        
        # Check each escalation category
        for category, keywords in self.ESCALATION_RULES.items():
            matches = sum(1 for keyword in keywords if keyword in message_lower)
            
            if matches > 0:
                reasons.append(f"{category}_detected")
                
                # Priority scoring
                if category == 'urgent':
                    priority_score += 3
                elif category == 'complaint':
                    priority_score += 2
                elif category == 'pricing':
                    priority_score += 2
                elif category == 'human_request':
                    priority_score += 1
        
        # Determine if escalation needed
        should_escalate = len(reasons) >= self.escalation_threshold
        
        # Determine priority
        if priority_score >= 3:
            priority = Priority.URGENT
        elif priority_score >= 2:
            priority = Priority.HIGH
        elif priority_score >= 1:
            priority = Priority.MEDIUM
        else:
            priority = Priority.LOW
        
        return {
            'should_escalate': should_escalate,
            'priority': priority.value,
            'reasons': reasons,
            'confidence': self._calculate_confidence(matches=len(reasons))
        }
    
    def _calculate_confidence(self, matches: int) -> str:
        """Calculate confidence level based on matches"""
        if matches >= 3:
            return 'high'
        elif matches >= 1:
            return 'medium'
        else:
            return 'low'
    
    def get_channel_response_rules(self, channel: str) -> Dict:
        """Get response formatting rules for channel"""
        return self.CHANNEL_RULES.get(channel, self.CHANNEL_RULES['web_form'])
    
    def format_response_for_channel(self, response: str, channel: str) -> str:
        """Format response according to channel rules"""
        rules = self.get_channel_response_rules(channel)
        
        # Truncate if too long
        if len(response) > rules['max_length']:
            response = response[:rules['max_length'] - 3] + '...'
        
        # Adjust tone (basic implementation)
        if rules['tone'] == 'casual' and channel == 'whatsapp':
            # Add friendly emoji for WhatsApp
            if not response.endswith('!') and not response.endswith('.'):
                response += ' 👍'
        
        return response
    
    def get_routing_decision(self, message: str, channel: str) -> Dict:
        """
        Complete routing decision with all details
        """
        analysis = self.analyze_message(message)
        channel_rules = self.get_channel_response_rules(channel)
        
        return {
            **analysis,
            'channel': channel,
            'channel_rules': channel_rules,
            'action': 'escalate' if analysis['should_escalate'] else 'ai_handle',
            'sla': channel_rules['response_time']
        }


# Sentiment Analysis (Basic)
def simple_sentiment_analysis(text: str) -> str:
    """
    Simple sentiment analysis
    Returns: 'positive', 'neutral', 'negative'
    """
    positive_words = [
        'great', 'good', 'excellent', 'amazing', 'love', 'happy',
        'satisfied', 'helpful', 'thanks', 'thank you', 'awesome'
    ]
    
    negative_words = [
        'bad', 'terrible', 'horrible', 'worst', 'hate', 'angry',
        'frustrated', 'disappointed', 'useless', 'waste', 'poor'
    ]
    
    text_lower = text.lower()
    
    positive_score = sum(1 for word in positive_words if word in text_lower)
    negative_score = sum(1 for word in negative_words if word in text_lower)
    
    if positive_score > negative_score:
        return 'positive'
    elif negative_score > positive_score:
        return 'negative'
    else:
        return 'neutral'


# Test the routing rules
if __name__ == "__main__":
    router = RoutingRules()
    
    test_messages = [
        ("How long does shipping take?", "web_form"),
        ("I'm very angry about the delay!", "whatsapp"),
        ("I want to speak to a manager", "email"),
        ("This is urgent! Need help immediately", "web_form"),
        ("Great service, thank you!", "whatsapp"),
        ("I want a refund for my order", "email")
    ]
    
    print("Routing Rules Test\n" + "="*60)
    for message, channel in test_messages:
        decision = router.get_routing_decision(message, channel)
        sentiment = simple_sentiment_analysis(message)
        
        print(f"\nMessage: {message}")
        print(f"Channel: {channel}")
        print(f"Sentiment: {sentiment}")
        print(f"Action: {decision['action'].upper()}")
        print(f"Priority: {decision['priority']}")
        print(f"Reasons: {', '.join(decision['reasons']) if decision['reasons'] else 'None'}")
