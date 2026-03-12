-- Initialize database with pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create enum types
CREATE TYPE channel_type AS ENUM ('email', 'whatsapp', 'web_form');
CREATE TYPE ticket_status AS ENUM ('open', 'in_progress', 'resolved', 'escalated');
CREATE TYPE message_priority AS ENUM ('low', 'medium', 'high', 'urgent');
CREATE TYPE sentiment_type AS ENUM ('positive', 'neutral', 'negative');

-- Customers table
CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    phone VARCHAR(50) UNIQUE,
    customer_type VARCHAR(50) DEFAULT 'individual',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

-- Customer identifiers for cross-channel tracking
CREATE TABLE IF NOT EXISTS customer_identifiers (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id) ON DELETE CASCADE,
    channel channel_type NOT NULL,
    identifier VARCHAR(255) NOT NULL,
    is_primary BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(customer_id, channel, identifier)
);

-- Knowledge base with vector embeddings
CREATE TABLE IF NOT EXISTS knowledge_base (
    id SERIAL PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    category VARCHAR(100),
    tags TEXT[],
    embedding vector(384),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usage_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true
);

-- Tickets table
CREATE TABLE IF NOT EXISTS tickets (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id) ON DELETE CASCADE,
    status ticket_status DEFAULT 'open',
    channel channel_type NOT NULL,
    subject VARCHAR(500),
    priority message_priority DEFAULT 'medium',
    sentiment sentiment_type DEFAULT 'neutral',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_to_human BOOLEAN DEFAULT false,
    assigned_to_agent INTEGER,
    resolved_at TIMESTAMP,
    first_response_time INTERVAL,
    resolution_time INTERVAL,
    metadata JSONB DEFAULT '{}'
);

-- Conversations (groups related messages)
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    ticket_id INTEGER REFERENCES tickets(id) ON DELETE CASCADE,
    session_id VARCHAR(255) UNIQUE,
    status VARCHAR(50) DEFAULT 'active',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    message_count INTEGER DEFAULT 0,
    last_message_at TIMESTAMP,
    context_summary TEXT,
    metadata JSONB DEFAULT '{}'
);

-- Messages table
CREATE TABLE IF NOT EXISTS messages (
    id SERIAL PRIMARY KEY,
    ticket_id INTEGER REFERENCES tickets(id) ON DELETE CASCADE,
    conversation_id INTEGER REFERENCES conversations(id) ON DELETE SET NULL,
    content TEXT NOT NULL,
    content_html TEXT,
    is_from_customer BOOLEAN DEFAULT true,
    channel channel_type NOT NULL,
    message_type VARCHAR(50) DEFAULT 'text',
    ai_generated BOOLEAN DEFAULT false,
    ai_model VARCHAR(100),
    ai_confidence FLOAT,
    sentiment sentiment_type DEFAULT 'neutral',
    sentiment_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

-- Channel configurations
CREATE TABLE IF NOT EXISTS channel_configs (
    id SERIAL PRIMARY KEY,
    channel channel_type UNIQUE NOT NULL,
    enabled BOOLEAN DEFAULT true,
    config JSONB DEFAULT '{}',
    rate_limit INTEGER DEFAULT 100,
    rate_limit_period INTEGER DEFAULT 60,
    auto_response_enabled BOOLEAN DEFAULT true,
    escalation_keywords TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Agent metrics
CREATE TABLE IF NOT EXISTS agent_metrics (
    id SERIAL PRIMARY KEY,
    date DATE DEFAULT CURRENT_DATE,
    channel channel_type,
    total_messages INTEGER DEFAULT 0,
    ai_handled INTEGER DEFAULT 0,
    human_escalated INTEGER DEFAULT 0,
    avg_response_time_ms INTEGER DEFAULT 0,
    avg_resolution_time_min INTEGER DEFAULT 0,
    customer_satisfaction FLOAT,
    accuracy_rate FLOAT,
    escalation_rate FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, channel)
);

-- Escalation logs
CREATE TABLE IF NOT EXISTS escalation_logs (
    id SERIAL PRIMARY KEY,
    ticket_id INTEGER REFERENCES tickets(id) ON DELETE CASCADE,
    reason VARCHAR(255) NOT NULL,
    escalated_by VARCHAR(100) DEFAULT 'ai',
    escalated_to INTEGER,
    priority message_priority,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    resolution_notes TEXT
);

-- Create indexes for performance
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_customers_phone ON customers(phone);
CREATE INDEX idx_tickets_customer_id ON tickets(customer_id);
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_channel ON tickets(channel);
CREATE INDEX idx_messages_ticket_id ON messages(ticket_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_knowledge_base_embedding ON knowledge_base USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX idx_conversations_ticket_id ON conversations(ticket_id);
CREATE INDEX idx_conversations_session_id ON conversations(session_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for updated_at
CREATE TRIGGER update_customers_updated_at BEFORE UPDATE ON customers
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tickets_updated_at BEFORE UPDATE ON tickets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_knowledge_base_updated_at BEFORE UPDATE ON knowledge_base
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_channel_configs_updated_at BEFORE UPDATE ON channel_configs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default channel configurations
INSERT INTO channel_configs (channel, config, escalation_keywords) VALUES
    ('email', '{"max_length": 1000, "tone": "formal", "signature": "Customer Support Team"}'::jsonb, 
     ARRAY['angry', 'refund', 'legal', 'manager', 'urgent']),
    ('whatsapp', '{"max_length": 160, "tone": "casual", "emoji_allowed": true}'::jsonb,
     ARRAY['angry', 'refund', 'legal', 'manager', 'urgent']),
    ('web_form', '{"max_length": 500, "tone": "professional", "show_ticket_id": true}'::jsonb,
     ARRAY['angry', 'refund', 'legal', 'manager', 'urgent']);

-- Insert sample knowledge base entries
INSERT INTO knowledge_base (question, answer, category, tags) VALUES
    ('What is your return policy?', 
     'We offer a 30-day return policy for all unused items in original packaging. Refunds are processed within 5-7 business days.',
     'returns', ARRAY['return', 'refund', 'policy']),
    ('How long does shipping take?',
     'Standard shipping takes 3-5 business days. Express shipping (1-2 business days) is available for an additional fee.',
     'shipping', ARRAY['shipping', 'delivery', 'time']),
    ('What payment methods do you accept?',
     'We accept all major credit cards (Visa, MasterCard, Amex), PayPal, and bank transfers for bulk orders.',
     'payment', ARRAY['payment', 'card', 'pay']);

-- Create view for ticket summary
CREATE VIEW ticket_summary AS
SELECT 
    t.id,
    t.status,
    t.channel,
    t.priority,
    t.sentiment,
    c.name as customer_name,
    c.email as customer_email,
    COUNT(m.id) as message_count,
    t.created_at,
    t.updated_at
FROM tickets t
LEFT JOIN customers c ON t.customer_id = c.id
LEFT JOIN messages m ON t.id = m.ticket_id
GROUP BY t.id, c.name, c.email;

-- Grant permissions (for production)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
