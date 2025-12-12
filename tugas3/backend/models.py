from sqlalchemy import (
    Column, Integer, Text, String, DateTime, func
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import register

# Setup SQLAlchemy Session
DBSession = scoped_session(sessionmaker())
register(DBSession)
Base = declarative_base()

class Review(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True)
    product_text = Column(Text, nullable=False)
    sentiment = Column(String(50))  # Positive/Negative/Neutral
    key_points = Column(Text)       # Hasil dari Gemini
    created_at = Column(DateTime, default=func.now())

    def to_json(self):
        return {
            'id': self.id,
            'text': self.product_text,
            'sentiment': self.sentiment,
            'key_points': self.key_points,
            'created_at': self.created_at.isoformat()
        }
