from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, BigInteger, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class UserStats(Base):
    __tablename__ = 'user_stats'
    
    user_id = Column(BigInteger, primary_key=True)
    username = Column(String)
    nickname = Column(String)
    total_messages = Column(Integer, default=0)
    toxic_messages = Column(Integer, default=0)
    positive_messages = Column(Integer, default=0)
    questions_asked = Column(Integer, default=0)
    responses_to_others = Column(Integer, default=0)
    flood_warnings = Column(Integer, default=0)
    rule_violations = Column(Integer, default=0)
    last_message_time = Column(DateTime)
    toxicity_sum = Column(Float, default=0)
    positivity_sum = Column(Float, default=0)
    activity_score = Column(Float, default=0)
    curiosity_score = Column(Float, default=0)
    responsiveness_score = Column(Float, default=0)
    character_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    messages = relationship("MessageHistory", back_populates="user")

class MessageHistory(Base):
    __tablename__ = 'message_history'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('user_stats.user_id'))
    username = Column(String)
    nickname = Column(String)
    message_text = Column(String)
    is_question = Column(Boolean, default=False)
    is_response = Column(Boolean, default=False)
    toxicity_level = Column(Float)
    positivity_level = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("UserStats", back_populates="messages") 