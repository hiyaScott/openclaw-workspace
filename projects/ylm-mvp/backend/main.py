from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import os

from models import init_db, get_db, User, Exercise, Submission

app = FastAPI(title="YLM MVP API", version="0.1.0")

# CORS - 允许所有来源
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化数据库
init_db()

# ============ Pydantic Models ============

class ExerciseCreate(BaseModel):
    title: str
    source_text: str
    reference_translation: Optional[str] = None
    source_lang: str = "zh"
    target_lang: str = "en"
    difficulty: str = "intermediate"
    text_type: Optional[str] = None
    theme: Optional[str] = None
    knowledge_points: Optional[str] = None
    direction: str = "zh-en"

class ExerciseOut(BaseModel):
    id: int
    title: str
    source_text: str
    source_lang: str
    target_lang: str
    difficulty: str
    text_type: Optional[str]
    direction: str
    
    class Config:
        from_attributes = True

class SubmissionCreate(BaseModel):
    exercise_id: int
    student_translation: str
    time_spent_seconds: int = 0
    pre_analysis: Optional[Dict] = None
    pre_submit_checklist: Optional[Dict] = None
    self_assessment: Optional[Dict] = None

class SubmissionOut(BaseModel):
    id: int
    exercise_id: int
    student_translation: str
    status: str
    ai_score: Optional[float]
    ai_feedback: Optional[Dict]
    created_at: datetime
    
    class Config:
        from_attributes = True

class ColdReviewData(BaseModel):
    checklist: Dict[str, bool]
    notes: Optional[str] = None

# ============ API Endpoints ============

@app.get("/api/status")
def root():
    return {"message": "YLM MVP API", "version": "0.1.0"}

# ---- Exercises ----

@app.get("/api/exercises", response_model=List[ExerciseOut])
def list_exercises(db: Session = Depends(get_db)):
    return db.query(Exercise).filter(Exercise.is_published == True).all()

@app.get("/api/exercises/{exercise_id}", response_model=ExerciseOut)
def get_exercise(exercise_id: int, db: Session = Depends(get_db)):
    ex = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not ex:
        raise HTTPException(404, "Exercise not found")
    return ex

@app.post("/api/exercises", response_model=ExerciseOut)
def create_exercise(data: ExerciseCreate, db: Session = Depends(get_db)):
    ex = Exercise(**data.dict())
    db.add(ex)
    db.commit()
    db.refresh(ex)
    return ex

# ---- Submissions ----

@app.post("/api/submissions", response_model=SubmissionOut)
def create_submission(data: SubmissionCreate, db: Session = Depends(get_db)):
    # 检查exercise存在
    ex = db.query(Exercise).filter(Exercise.id == data.exercise_id).first()
    if not ex:
        raise HTTPException(404, "Exercise not found")
    
    sub = Submission(
        exercise_id=data.exercise_id,
        user_id=1,  # MVP阶段固定用户
        student_translation=data.student_translation,
        time_spent_seconds=data.time_spent_seconds,
        pre_analysis=data.pre_analysis,
        pre_submit_checklist=data.pre_submit_checklist,
        self_assessment=data.self_assessment,
        status="submitted"
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return sub

@app.get("/api/submissions/{submission_id}", response_model=SubmissionOut)
def get_submission(submission_id: int, db: Session = Depends(get_db)):
    sub = db.query(Submission).filter(Submission.id == submission_id).first()
    if not sub:
        raise HTTPException(404, "Submission not found")
    return sub

@app.post("/api/submissions/{submission_id}/grade")
def grade_submission(submission_id: int, db: Session = Depends(get_db)):
    """触发AI评分（MVP阶段简化版）"""
    sub = db.query(Submission).filter(Submission.id == submission_id).first()
    if not sub:
        raise HTTPException(404, "Submission not found")
    
    ex = db.query(Exercise).filter(Exercise.id == sub.exercise_id).first()
    
    # MVP阶段：简化评分（后续接入DeepSeek API）
    # 这里先返回一个mock评分，让用户看到报告格式
    mock_feedback = {
        "score": 8.5,
        "max_score": 15,
        "band": "良好表达",
        "next_step": "重点检查主语选择和逻辑显化",
        "strategy_focus": "主语选择",
        "first_fix": "第2行'it is important'改为'it matters'更简洁",
        "errors": [
            {
                "code": "O",
                "category": "意义传递",
                "severity": "中等",
                "source_text": "取得了显著进展",
                "student_text": "made progress",
                "suggestion": "漏译了'显著'，建议改为 made remarkable progress",
                "montreal_diagnosis": "信息点核对不足"
            },
            {
                "code": "SYN",
                "category": "译入语规范",
                "severity": "轻微",
                "source_text": "发挥着重要作用",
                "student_text": "plays an important role",
                "suggestion": "语法正确，但可考虑 plays a crucial role 提升正式度",
                "montreal_diagnosis": "语域控制"
            }
        ],
        "phrase_suggestions": [
            {
                "source": "取得了显著进展",
                "neutral": "achieved significant progress",
                "formal": "made remarkable strides",
                "colloquial": "come a long way"
            }
        ],
        "core_competencies": {
            "语言能力": "发展中",
            "文化意识": "达标",
            "思维品质": "达标",
            "学习能力": "发展中"
        },
        "process_diagnosis": "接稿分析完成度良好，建议加强自审环节",
        "reference_versions": {
            "neutral": "China has achieved significant progress in environmental protection.",
            "formal": "The People's Republic of China has made remarkable strides in the domain of environmental conservation.",
            "colloquial": "China's come a long way in protecting the environment."
        }
    }
    
    sub.ai_score = mock_feedback["score"]
    sub.ai_feedback = mock_feedback
    sub.status = "graded"
    sub.graded_at = datetime.utcnow()
    db.commit()
    
    return {"message": "评分完成", "submission_id": submission_id, "feedback": mock_feedback}

@app.post("/api/submissions/{submission_id}/cold-review")
def submit_cold_review(submission_id: int, data: ColdReviewData, db: Session = Depends(get_db)):
    sub = db.query(Submission).filter(Submission.id == submission_id).first()
    if not sub:
        raise HTTPException(404, "Submission not found")
    sub.cold_review = data.dict()
    db.commit()
    return {"message": "冷审稿已记录"}

# ---- Init sample data ----

@app.post("/api/init-data")
def init_sample_data(db: Session = Depends(get_db)):
    """初始化示例数据"""
    # 检查是否已有数据
    if db.query(Exercise).first():
        return {"message": "数据已存在"}
    
    exercises = [
        Exercise(
            title="CET-4 真题：环境保护",
            source_text="近年来，中国政府在环境保护方面取得了显著进展。通过实施一系列严格的环保政策，中国的空气质量得到了明显改善。",
            reference_translation="In recent years, the Chinese government has achieved significant progress in environmental protection. Through the implementation of a series of strict environmental policies, China's air quality has been markedly improved.",
            source_lang="zh",
            target_lang="en",
            difficulty="intermediate",
            text_type="社会发展类",
            theme="环境保护",
            exam_type="cet",
            direction="zh-en"
        ),
        Exercise(
            title="CET-4 真题：传统文化",
            source_text="春节是中国最重要的传统节日。每逢春节，无论身在何处，人们都会尽力回家与家人团聚，共度佳节。",
            reference_translation="The Spring Festival is the most important traditional festival in China. During the Spring Festival, no matter where they are, people will try their best to return home and reunite with their families to celebrate the festival.",
            source_lang="zh",
            target_lang="en",
            difficulty="beginner",
            text_type="文化介绍类",
            theme="传统文化",
            exam_type="cet",
            direction="zh-en"
        ),
        Exercise(
            title="CET-6 真题：科技创新",
            source_text="人工智能正在深刻改变我们的生活方式。从智能手机到自动驾驶汽车，AI技术已经渗透到日常生活的方方面面。",
            reference_translation="Artificial intelligence is profoundly changing our way of life. From smartphones to self-driving cars, AI technology has permeated every aspect of daily life.",
            source_lang="zh",
            target_lang="en",
            difficulty="advanced",
            text_type="科技生活类",
            theme="科技创新",
            exam_type="cet",
            direction="zh-en"
        )
    ]
    
    for ex in exercises:
        db.add(ex)
    
    db.commit()
    return {"message": "示例数据已创建", "count": len(exercises)}

# ---- Static Files (前端) ----

STATIC_DIR = os.path.join(os.path.dirname(__file__), "../frontend/dist")
if os.path.exists(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
