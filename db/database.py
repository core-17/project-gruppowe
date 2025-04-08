import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# Створюємо шлях до бази даних у папці db
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR)  # Виправлено: прибрано зайвий 'db'
DATABASE_URL = f"sqlite:///{os.path.join(DB_DIR, 'bot_database.db')}"

# Налаштування SQLAlchemy
engine = create_engine(DATABASE_URL, echo=True)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Моделі бази даних
class UserStats(Base):
    __tablename__ = "user_stats"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)
    tips_given = Column(Integer, default=0)
    tips_received = Column(Integer, default=0)
    actions = relationship("UserAction", back_populates="user")

class UserAction(Base):
    __tablename__ = "user_actions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("user_stats.user_id"))
    action = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user = relationship("UserStats", back_populates="actions")

# Ініціалізація бази даних
def init_db():
    Base.metadata.create_all(bind=engine)