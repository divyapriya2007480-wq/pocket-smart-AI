from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator


PlannerType = Literal["home", "party", "jewelry"]


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class HomePlannerInput(BaseModel):
    budget: float = Field(gt=0, le=100_000_000)
    currency: str = Field(default="INR", min_length=3, max_length=3)
    rooms: str = Field(min_length=2, max_length=300)
    style: str = Field(default="Modern", min_length=2, max_length=100)
    required_items: str = Field(min_length=2, max_length=1000)
    notes: str = Field(default="", max_length=1000)


class PartyPlannerInput(BaseModel):
    budget: float = Field(gt=0, le=100_000_000)
    currency: str = Field(default="INR", min_length=3, max_length=3)
    guest_count: int = Field(gt=0, le=100_000)
    event_type: str = Field(min_length=2, max_length=100)
    venue_preference: str = Field(default="No preference", max_length=200)
    food_preference: str = Field(default="Mixed", max_length=100)
    city: str = Field(min_length=2, max_length=100)
    notes: str = Field(default="", max_length=1000)


class JewelryPlannerInput(BaseModel):
    budget: float = Field(gt=0, le=100_000_000)
    currency: str = Field(default="INR", min_length=3, max_length=3)
    occasion: str = Field(min_length=2, max_length=100)
    style: str = Field(default="Elegant", max_length=100)
    outfit_description: str = Field(default="", max_length=1000)
    preferred_material: str = Field(default="No preference", max_length=100)
    notes: str = Field(default="", max_length=1000)


class RecommendationItem(BaseModel):
    category: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=600)
    estimated_price: float = Field(ge=0)
    platform: str = Field(min_length=1, max_length=100)
    search_query: str = Field(min_length=1, max_length=300)
    priority: Literal["essential", "recommended", "optional"] = "recommended"

    @field_validator("estimated_price")
    @classmethod
    def round_price(cls, value: float) -> float:
        return round(value, 2)


class BudgetAllocation(BaseModel):
    category: str = Field(min_length=1, max_length=100)
    amount: float = Field(ge=0)
    percentage: float = Field(ge=0, le=100)


class RecommendationPlan(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    summary: str = Field(min_length=1, max_length=1200)
    total_budget: float = Field(gt=0)
    estimated_total: float = Field(ge=0)
    currency: str = Field(min_length=3, max_length=3)
    allocations: list[BudgetAllocation]
    recommendations: list[RecommendationItem]
    money_saving_tips: list[str]
    assumptions: list[str]
    warning: str = ""
