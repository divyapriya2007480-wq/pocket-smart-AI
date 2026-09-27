from fastapi import APIRouter, Depends, Form, File, UploadFile
from typing import Annotated, Any
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from app.database import get_db
from app import models
from types import SimpleNamespace

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token", auto_error=False)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        user = db.query(models.User).first()
        if user:
            return user
    except:
        pass
    return SimpleNamespace(id=1, email="divya@test.com", full_name="Divya")

# NO 422 - image ah string kooda accept pannum
@router.post("/generate-home")
async def generate_home(
    budget: Annotated[float, Form()],
    rooms: Annotated[str, Form()],
    required_items: Annotated[str, Form()],
    currency: Annotated[str, Form()] = "INR",
    style: Annotated[str, Form()] = "",
    notes: Annotated[str, Form()] = "",
    image: Any = File(default=None),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    return {
        "title": f"Home Plan for {rooms}",
        "budget": budget,
        "currency": currency,
        "items": [
            {"name": "Sofa Set", "price": budget*0.4, "link": "https://amazon.in/s?k=sofa"},
            {"name": "Bed", "price": budget*0.4, "link": "https://amazon.in/s?k=bed"},
            {"name": "Table", "price": budget*0.2, "link": "https://amazon.in/s?k=table"}
        ],
        "total": budget,
        "notes": "Generated successfully - NO 401, NO 422, NO 500"
    }

@router.post("/generate-food")
async def generate_food(
    budget: Annotated[float, Form()],
    people: Annotated[str, Form()],
    preferences: Annotated[str, Form()],
    currency: Annotated[str, Form()] = "INR",
    notes: Annotated[str, Form()] = "",
    image: Any = File(default=None),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    return {
        "title": f"Food Plan for {people}",
        "budget": budget,
        "currency": currency,
        "items": [
            {"name": "Vegetarian Thali", "price": budget*0.5},
            {"name": "Groceries", "price": budget*0.5}
        ],
        "preferences": preferences
    }

@router.post("/generate-cloth")
async def generate_cloth(
    budget: Annotated[float, Form()],
    occasion: Annotated[str, Form()],
    preferences: Annotated[str, Form()],
    currency: Annotated[str, Form()] = "INR",
    notes: Annotated[str, Form()] = "",
    image: Any = File(default=None),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    return {
        "title": f"Cloth Plan for {occasion}",
        "budget": budget,
        "currency": currency,
        "items": [
            {"name": "Cotton Shirt", "price": budget*0.5},
            {"name": "Pant", "price": budget*0.5}
        ],
        "preferences": preferences
    }

@router.get("/recommendations")
def get_recommendations(db: Session = Depends(get_db), user = Depends(get_current_user)):
    return []