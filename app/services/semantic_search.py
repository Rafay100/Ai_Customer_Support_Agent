"""
Semantic Search using pgvector and sentence-transformers
For production-grade knowledge base search
"""
import os
from typing import List, Dict, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
import numpy as np

class SemanticSearchService:
    def __init__(self):
        self.enabled = False
        self.model = None
        self.database_url = os.getenv("DATABASE_URL", "")
        
        # Check if PostgreSQL with pgvector is available
        if "postgresql" in self.database_url:
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                self.enabled = True
                print("[OK] Semantic search enabled with pgvector")
            except Exception as e:
                print(f"[WARN] Semantic search disabled: {e}")
                self.enabled = False
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for text"""
        if not self.enabled or not self.model:
            return []
        
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []
    
    def search_knowledge_base(
        self, 
        query: str, 
        limit: int = 5,
        db_session: Optional[Session] = None
    ) -> List[Dict]:
        """
        Search knowledge base using semantic similarity
        Returns most relevant FAQs
        """
        if not self.enabled:
            return []
        
        try:
            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            
            if not db_session:
                return []
            
            # Search using pgvector cosine similarity
            from app.models.models import KnowledgeBase
            from sqlalchemy import desc
            
            # Convert embedding to string for PostgreSQL
            embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
            
            results = db_session.execute(
                text("""
                    SELECT id, question, answer, category, tags, 
                           1 - (embedding <=> :embedding::vector) as similarity
                    FROM knowledge_base
                    WHERE is_active = true
                    ORDER BY similarity DESC
                    LIMIT :limit
                """),
                {"embedding": embedding_str, "limit": limit}
            ).fetchall()
            
            return [
                {
                    "id": r.id,
                    "question": r.question,
                    "answer": r.answer,
                    "category": r.category,
                    "tags": r.tags,
                    "similarity": r.similarity
                }
                for r in results
                if r.similarity > 0.3  # Minimum similarity threshold
            ]
            
        except Exception as e:
            print(f"Semantic search error: {e}")
            return []
    
    def find_best_match(self, query: str, db_session: Optional[Session] = None) -> Optional[Dict]:
        """Find best matching FAQ"""
        results = self.search_knowledge_base(query, limit=1, db_session=db_session)
        return results[0] if results else None
    
    def update_embedding(self, kb_id: int, text: str, db_session: Session):
        """Update embedding for a knowledge base entry"""
        if not self.enabled:
            return
        
        embedding = self.generate_embedding(text)
        embedding_str = '[' + ','.join(map(str, embedding)) + ']'
        
        db_session.execute(
            text("""
                UPDATE knowledge_base 
                SET embedding = :embedding::vector 
                WHERE id = :id
            """),
            {"embedding": embedding_str, "id": kb_id}
        )
        db_session.commit()


# Global instance
semantic_search = SemanticSearchService()
