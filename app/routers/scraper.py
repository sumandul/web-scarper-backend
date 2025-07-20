from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Query, Request,status
from fastapi.responses import StreamingResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import List
from uuid import uuid4
import asyncio
import json

from app.schemas.scraper import ScrapeRequest, ScrapeResponse
from app.services.scraper_service import perform_scraping
from app.core.database import get_db
from app.models.scraper import ScrapeJob

router = APIRouter()

# 🧠 Background function
def run_scraper(job_id: str, url: str, scraper_type: str, tags: list[str]):
    db = next(get_db())
    try:
        result = perform_scraping(url, scraper_type)
        safe_data = jsonable_encoder(result.get("data", {}))

        job = db.query(ScrapeJob).filter(ScrapeJob.id == job_id).first()
        if job:
            job.status = result.get("status", "completed")
            job.raw_html = safe_data.get("raw_html")
            job.llm_summary = safe_data.get("summary")
            job.headline = safe_data.get("headline")
            job.tldr = safe_data.get("tldr")
            job.topics = safe_data.get("topics")
            job.seo_tags = safe_data.get("seo_tags")
            job.entities = safe_data.get("entities")
            job.sentiment = safe_data.get("sentiment")
            job.tags = tags
            job.result = safe_data

            db.commit()
    except Exception as e:
        job = db.query(ScrapeJob).filter(ScrapeJob.id == job_id).first()
        if job:
            job.status = "error"
            job.result = {"error": str(e)}
            db.commit()
    finally:
        db.close()
async def get_current_user(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return user

# CREATE - start scraping job
@router.post("/add", response_model=ScrapeResponse)
def start_scrape(request: ScrapeRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db),   user: dict = Depends(get_current_user)):
    job_id = str(uuid4())
    job = ScrapeJob(
        id=job_id,
        url=str(request.url),
        scraper_type=request.scraper_type,
        status="in_progress",
        tags=request.tags,
         user_id=user.get("id")
        
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    background_tasks.add_task(run_scraper, job_id, str(request.url), request.scraper_type, request.tags)

    return ScrapeResponse(job_id=job_id, status=job.status, data={})


# SSE endpoint with full form data return upon completion
@router.get("/stream/{job_id}")
async def stream_scrape_status(job_id: str, request: Request, db: Session = Depends(get_db)):
    async def event_generator():
        while True:
            if await request.is_disconnected():
                break

            job = db.query(ScrapeJob).filter(ScrapeJob.id == job_id).first()
            print(job.status)

            if job:
                db.refresh(job) 
                if job.status == "completed":
                    result_data = job.result if isinstance(job.result, dict) else json.loads(job.result)
                    data = {
                        "job_id": str(job.id),
                        "status": job.status,
                        "url": job.url,
                        "scraper_type": job.scraper_type,
                        "tags": job.tags,
                        "result": result_data,
                    }
                    yield f"data: {json.dumps(data)}\n\n"
                    break
                elif job.status == "error":
                    data = {
                        "job_id": str(job.id),
                        "status": job.status,
                        "error": job.result.get("error") if isinstance(job.result, dict) else job.result
                    }
                    yield f"data: {json.dumps(data)}\n\n"
                    break
                else:
                    yield f"data: {json.dumps({"status": job.status})}\n\n"
            await asyncio.sleep(2)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/scrape/status/{job_id}")
def get_scrape_status(job_id: str, db: Session = Depends(get_db)):
    job = db.query(ScrapeJob).filter(ScrapeJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "job_id": str(job.id),
        "status": job.status,
        "result": job.result if job.status == "completed" else None
    }


@router.get("/list", response_model=List[ScrapeResponse])
def list_scrape_jobs(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1), db: Session = Depends(get_db)):
    jobs = db.query(ScrapeJob).offset(skip).limit(limit).all()
    result = []
    for job in jobs:
        data = job.result if isinstance(job.result, dict) else json.loads(job.result) if job.result else {}
        result.append(ScrapeResponse(job_id=str(job.id), status=job.status, data=data))
    return result


@router.get("/{job_id}", response_model=ScrapeResponse)
def get_scrape_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(ScrapeJob).filter(ScrapeJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    data = job.result if isinstance(job.result, dict) else json.loads(job.result) if job.result else {}
    return ScrapeResponse(job_id=str(job.id), status=job.status, data=data)


@router.put("/{job_id}", response_model=ScrapeResponse)
def update_scrape_job(job_id: str, request: ScrapeRequest, db: Session = Depends(get_db)):
    job = db.query(ScrapeJob).filter(ScrapeJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.url = str(request.url)
    job.scraper_type = request.scraper_type
    db.commit()
    db.refresh(job)
    data = job.result if isinstance(job.result, dict) else json.loads(job.result) if job.result else {}
    return ScrapeResponse(job_id=str(job.id), status=job.status, data=data)


@router.delete("/{job_id}", status_code=204)
def delete_scrape_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(ScrapeJob).filter(ScrapeJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(job)
    db.commit()
    return None
