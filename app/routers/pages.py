from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import BASE_DIR, settings
from app.database import get_db
from app.dependencies import get_session_user, require_session_user
from app.models import Recommendation, User


router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))


def context(request: Request, user: User | None = None, **kwargs):
    return {
        "request": request,
        "app_name": settings.app_name,
        "current_user": user,
        **kwargs,
    }


@router.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=context(request, get_session_user(request, db)),
    )


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request, db: Session = Depends(get_db)):
    if get_session_user(request, db):
        return RedirectResponse("/dashboard", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context=context(request, error=request.query_params.get("error")),
    )


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, db: Session = Depends(get_db)):
    if get_session_user(request, db):
        return RedirectResponse("/dashboard", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context=context(request, error=request.query_params.get("error")),
    )


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_session_user),
):
    recent = db.scalars(
        select(Recommendation)
        .where(Recommendation.user_id == user.id)
        .order_by(Recommendation.created_at.desc())
        .limit(5)
    ).all()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context=context(request, user, recent=recent),
    )


@router.get("/planner/{planner_type}", response_class=HTMLResponse)
def planner(
    planner_type: str,
    request: Request,
    user: User = Depends(require_session_user),
):
    if planner_type not in {"home", "party", "jewelry"}:
        raise HTTPException(status_code=404, detail="Planner not found")

    return templates.TemplateResponse(
        request=request,
        name="planner.html",
        context=context(
            request,
            user,
            planner_type=planner_type,
            error=request.query_params.get("error"),
        ),
    )


@router.get("/recommendations/{recommendation_id}", response_class=HTMLResponse)
def recommendation_details(
    recommendation_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_session_user),
):
    record = db.scalar(
        select(Recommendation).where(
            Recommendation.id == recommendation_id,
            Recommendation.user_id == user.id,
        )
    )
    if not record:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    return templates.TemplateResponse(
        request=request,
        name="results.html",
        context=context(request, user, record=record, plan=record.response_data),
    )


@router.get("/history", response_class=HTMLResponse)
def history(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(require_session_user),
):
    records = db.scalars(
        select(Recommendation)
        .where(Recommendation.user_id == user.id)
        .order_by(Recommendation.created_at.desc())
    ).all()

    return templates.TemplateResponse(
        request=request,
        name="history.html",
        context=context(request, user, records=records),
    )
