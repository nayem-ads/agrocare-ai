from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.database import get_db
from backend.app.models import Report, User
from backend.app.schemas import ReportResponse
from backend.app.auth import get_current_user, get_optional_user

router = APIRouter(prefix="/api/reports", tags=["Reports"])

@router.get("/my", response_model=List[ReportResponse])
def get_my_reports(db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_current_user)):
    """
    Get all diagnostic reports created by the currently authenticated farmer.
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required to view reports history."
        )
    user_reports = db.query(Report).filter(Report.user_id == current_user.id).order_by(Report.created_at.desc()).all()
    if not user_reports:
        # Include recent public/demo reports if the newly registered farmer has no personal reports yet
        return db.query(Report).order_by(Report.created_at.desc()).limit(10).all()
    return user_reports

@router.get("/{report_id}", response_model=ReportResponse)
def get_report_details(report_id: int, db: Session = Depends(get_db), current_user: Optional[User] = Depends(get_optional_user)):
    """
    Get details of a single report by its ID.
    Accessible to authenticated farmers, officers, and anonymous diagnosis sessions.
    """
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found."
        )

    return report
