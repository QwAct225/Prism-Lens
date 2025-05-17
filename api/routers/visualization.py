from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
import os
from fastapi.responses import FileResponse

from api.models.papers import PaperResponse
from api.services.visualization import VisualizationService

router = APIRouter()
visualization_service = VisualizationService()

@router.get("/plots", response_model=List[str])
async def list_plots():
    """
    List all available visualization plots.
    """
    try:
        plots = visualization_service.list_plots()
        return plots
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/plot/{plot_name}")
async def get_plot(plot_name: str):
    """
    Get a specific visualization plot as an image.
    """
    try:
        plot_path = visualization_service.get_plot_path(plot_name)
        if not os.path.exists(plot_path):
            raise HTTPException(status_code=404, detail=f"Plot {plot_name} not found")
        return FileResponse(plot_path)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/papers")
async def get_papers(
    limit: int = Query(10, description="Maximum number of papers to return"),
    skip: int = Query(0, description="Number of papers to skip"),
    search: Optional[str] = Query(None, description="Search term to filter papers by title or author"),
    sort_by: Optional[str] = Query(None, description="Field to sort by"),
    sort_order: Optional[str] = Query("asc", description="Sort order (asc or desc)")
):
    """
    Get papers from the cleaned dataset with pagination, searching, and sorting.
    """
    try:
        papers = visualization_service.get_papers(limit, skip, search, sort_by, sort_order)
        return papers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_statistics():
    """
    Get statistics about the paper dataset.
    """
    try:
        stats = visualization_service.get_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/embeddings")
async def get_embeddings(
    limit: int = Query(100, description="Maximum number of embeddings to return"),
    skip: int = Query(0, description="Number of embeddings to skip"),
):
    """
    Get paper embeddings for visualization.
    """
    try:
        embeddings = visualization_service.get_embeddings(limit, skip)
        return embeddings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))