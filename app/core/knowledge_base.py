# Product FAQs - Knowledge Base
# AI will search these to answer customer questions

FAQS = [
    {
        "question": "What is your return policy?",
        "answer": "We offer a 30-day return policy for all unused items in original packaging. Refunds are processed within 5-7 business days.",
        "keywords": ["return", "refund", "policy", "send back"]
    },
    {
        "question": "How long does shipping take?",
        "answer": "Standard shipping takes 3-5 business days. Express shipping (1-2 business days) is available for an additional fee.",
        "keywords": ["shipping", "delivery", "time", "how long"]
    },
    {
        "question": "What payment methods do you accept?",
        "answer": "We accept all major credit cards (Visa, MasterCard, Amex), PayPal, and bank transfers for bulk orders.",
        "keywords": ["payment", "card", "pay", "method"]
    },
    {
        "question": "Do you offer international shipping?",
        "answer": "Yes, we ship to over 50 countries. International shipping takes 7-14 business days. Customs duties may apply.",
        "keywords": ["international", "country", "worldwide", "abroad"]
    },
    {
        "question": "How can I track my order?",
        "answer": "Once your order ships, you'll receive a tracking number via email/SMS. Use it on our website or the carrier's site to track.",
        "keywords": ["track", "tracking", "order status", "where is my order"]
    },
    {
        "question": "Can I cancel my order?",
        "answer": "Orders can be cancelled within 24 hours of placement. After that, the order may have already shipped and returns process applies.",
        "keywords": ["cancel", "cancellation", "stop order"]
    },
    {
        "question": "What is your warranty policy?",
        "answer": "All products come with a 1-year manufacturer warranty covering defects. Extended warranty options available at checkout.",
        "keywords": ["warranty", "guarantee", "defect", "broken"]
    },
    {
        "question": "How do I contact customer support?",
        "answer": "Reach us via email at support@company.com, WhatsApp at +1-234-567-8900, or through our website contact form.",
        "keywords": ["contact", "support", "help", "reach"]
    },
    {
        "question": "Do you have a physical store?",
        "answer": "We are primarily online but have experience centers in major cities. Check our website for locations and hours.",
        "keywords": ["store", "shop", "location", "visit"]
    },
    {
        "question": "What are your business hours?",
        "answer": "Customer support is available Monday-Saturday, 9 AM - 6 PM EST. We respond to emails within 24 hours.",
        "keywords": ["hours", "time", "open", "available"]
    }
]

# Escalation triggers - when to forward to human
ESCALATION_KEYWORDS = [
    "angry", "frustrated", "complaint", "lawyer", "legal", "sue",
    "manager", "supervisor", "human", "real person", "terrible",
    "worst", "disappointed", "unacceptable", "refund immediately",
    "chargeback", "dispute", "cancel account"
]

# Pricing-related (should escalate)
PRICING_KEYWORDS = [
    "discount", "coupon", "promo code", "bulk pricing", "enterprise",
    "negotiate", "price match", "cheaper", "expensive"
]
