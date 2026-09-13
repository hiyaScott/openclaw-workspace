from sqlalchemy import create_engine, Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    nickname = Column(String, nullable=True)
    password_hash = Column(String)
    role = Column(String, default="student")  # student, teacher, admin
    created_at = Column(DateTime, default=datetime.utcnow)

class Exercise(Base):
    __tablename__ = "exercises"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    source_text = Column(Text)
    reference_translation = Column(Text, nullable=True)
    source_lang = Column(String, default="zh")
    target_lang = Column(String, default="en")
    difficulty = Column(String, default="intermediate")  # beginner, intermediate, advanced
    text_type = Column(String, nullable=True)
    theme = Column(String, nullable=True)
    knowledge_points = Column(Text, nullable=True)
    exam_type = Column(String, default="cet")
    direction = Column(String, default="zh-en")
    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    submissions = relationship("Submission", back_populates="exercise")

class Submission(Base):
    __tablename__ = "submissions"
    id = Column(Integer, primary_key=True, index=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    student_translation = Column(Text)
    time_spent_seconds = Column(Integer, default=0)
    
    # 翻译前分析
    pre_analysis = Column(JSON, nullable=True)
    
    # 提交前自审
    pre_submit_checklist = Column(JSON, nullable=True)
    
    # 提交后自评
    self_assessment = Column(JSON, nullable=True)
    
    # AI评分结果
    ai_score = Column(Float, nullable=True)
    ai_feedback = Column(JSON, nullable=True)
    status = Column(String, default="pending")  # pending, submitted, graded
    
    # 冷审稿
    cold_review = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    graded_at = Column(DateTime, nullable=True)
    
    exercise = relationship("Exercise", back_populates="submissions")

# SQLite数据库
engine = create_engine("sqlite:///./ylm.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
