# In your existing scraper router file
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.scraper import ScrapeJob
from app.models.chat_history import ChatHistory

router = APIRouter()

class ChatRequest(BaseModel):
    job_id: str
    question: str

class ChatResponse(BaseModel):
    answer: str

class ChatHistoryResponse(BaseModel):
    id: str
    job_id: str
    question: str
    response: str
    created_at: str

# Replace with your actual local LLaMA call
def query_local_llm(prompt: str) -> str:
    import requests
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "llama3", "prompt": prompt, "stream": False}
    )
    data = response.json()
    return data.get("response", "").strip()

@router.post("/add", response_model=ChatResponse)
def chat_on_summary(request: ChatRequest, db: Session = Depends(get_db)):
    print("hit")
    job = db.query(ScrapeJob).filter(ScrapeJob.id == request.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    summary = (
        job.llm_summary or
        job.tldr or
        (job.result.get("summary") if job.result and isinstance(job.result, dict) else None)
    )

    if not summary:
        raise HTTPException(status_code=400, detail="No summary available for this job.")

    prompt = (
        f"You are an assistant answering questions based on the following article summary:\n\n"
        f"{summary}\n\n"
        f"Question: {request.question}\n"
        f"Answer:"
    )

    answer = query_local_llm(prompt)
    # print(anse)

    # ✅ Save chat history
    chat_entry = ChatHistory(
        job_id=job.id,
        question=request.question,
        response=answer
    )
    db.add(chat_entry)
    db.commit()

    return ChatResponse(answer=answer)

@router.get("/history/{job_id}", response_model=List[ChatHistoryResponse])
def get_chat_history(job_id: str, db: Session = Depends(get_db)):
    job = db.query(ScrapeJob).filter(ScrapeJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    chats = (
        db.query(ChatHistory)
        .filter(ChatHistory.job_id == job_id)
        .order_by(ChatHistory.created_at.asc())
        .all()
    )

    return [
        ChatHistoryResponse(
            id=str(chat.id),
            job_id=str(chat.job_id),
            question=chat.question,
            response=chat.response,
            created_at=str(chat.created_at)
        )
        for chat in chats
    ]
