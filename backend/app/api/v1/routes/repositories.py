from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.repository import RepositoryCreateRequest, RepositoryResponse
from app.services.repository_service import RepositoryService

router = APIRouter(prefix="/repos", tags=["repositories"])


@router.post("", response_model=RepositoryResponse)
def create_repository(
    request: RepositoryCreateRequest,
    db: Session = Depends(get_db),
):
    try:
        service = RepositoryService(db)
        result = service.ingest_from_url(request.url)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))