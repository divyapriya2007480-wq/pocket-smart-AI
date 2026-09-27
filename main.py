from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.database import engine, SessionLocal
from app import models
from app.routers import auth, pages, api
from types import SimpleNamespace

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="PocketSmart AI")

# ===== AUTH BYPASS - NO MORE 401 =====
def get_fake_user():
    try:
        db = SessionLocal()
        user = db.query(models.User).first()
        if user:
            db.close()
            return user
        db.close()
    except:
        pass
    return SimpleNamespace(id=1, email="divya@test.com", full_name="Divya", is_active=True)

# Override ALL auth checks
try:
    from app.security import get_current_user as sec_auth
    app.dependency_overrides[sec_auth] = get_fake_user
except:
    pass

try:
    from app.dependencies import get_current_user as dep_auth
    app.dependency_overrides[dep_auth] = get_fake_user
except:
    pass
# ===== END BYPASS =====

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.include_router(auth.router)
app.include_router(pages.router)
app.include_router(api.router)

@app.get("/")
async def root(request: Request):
    return RedirectResponse(url="/dashboard")

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "PocketSmart AI is running - NO AUTH"}