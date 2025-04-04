from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Depends
from typing import List, Optional

from api.models.papers import ScrapingRequest, ScrapingResponse, ScrapingStatus
from api.services.scraping import ScrapingService

router = APIRouter()
scraping_service = ScrapingService()

@router.post("/start", response_model=ScrapingResponse)
async def start_scraping(request: ScrapingRequest, background_tasks: BackgroundTasks):
    """
    Start scraping ArXiv papers with specified parameters.
    """
    try:
        job_id = scraping_service.create_job(request)
        # Start the scraping process in the background
        background_tasks.add_task(scraping_service.run_scraping_job, job_id)
        return ScrapingResponse(job_id=job_id, status="started")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{job_id}", response_model=ScrapingStatus)
async def get_scraping_status(job_id: str):
    """
    Get the status of a scraping job.
    """
    try:
        status = scraping_service.get_job_status(job_id)
        if status is None:
            raise HTTPException(status_code=404, detail="Job not found")
        return status
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cancel/{job_id}")
async def cancel_scraping(job_id: str):
    """
    Cancel a running scraping job.
    """
    try:
        result = scraping_service.cancel_job(job_id)
        if not result:
            raise HTTPException(status_code=404, detail="Job not found or already completed")
        return {"message": f"Job {job_id} has been cancelled"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs", response_model=List[ScrapingStatus])
async def get_all_jobs(
    limit: int = Query(10, description="Maximum number of jobs to return"),
    skip: int = Query(0, description="Number of jobs to skip"),
    status: Optional[str] = Query(None, description="Filter by status (started, running, completed, failed, cancelled)")
):
    """
    Get all scraping jobs, with optional filtering by status.
    """
    try:
        jobs = scraping_service.get_all_jobs(limit, skip, status)
        return jobs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))