import asyncio
import json
from typing import Any

from google import genai
from google.genai import types

from app.config import settings
from app.schemas import RecommendationPlan


SYSTEM_RULES = """
You are PocketSmart AI, a careful budget-planning assistant.

Return a realistic plan that:
1. Never exceeds the user's total budget.
2. Treats prices as estimates, not verified live marketplace prices.
3. Uses only these platform labels when appropriate:
   Amazon, Flipkart, IKEA, Swiggy, Zomato, OYO, Local vendor.
4. Provides marketplace search queries, never invented product URLs.
5. Prioritizes essentials and preserves a contingency amount.
6. Does not claim availability, discounts, ratings, or exact current prices.
7. For jewelry, uses an uploaded image only for visible color/style coordination.
8. Includes practical assumptions and safety or purchasing warnings.
"""


class GeminiService:
    def __init__(self) -> None:
        self.enabled = bool(settings.gemini_api_key)
        self.client = (
            genai.Client(api_key=settings.gemini_api_key)
            if self.enabled
            else None
        )

    async def create_plan(
        self,
        planner_type: str,
        user_input: dict[str, Any],
        image_bytes: bytes | None = None,
        image_mime_type: str | None = None,
    ) -> RecommendationPlan | None:
        if not self.client:
            return None

        prompt = (
            f"{SYSTEM_RULES}\n\n"
            f"Planner type: {planner_type}\n"
            f"User input:\n{json.dumps(user_input, ensure_ascii=False, indent=2)}"
        )

        contents: list[Any] = [prompt]
        if image_bytes and image_mime_type:
            contents.append(
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=image_mime_type,
                )
            )

        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=settings.gemini_model,
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=0.35,
                    response_mime_type="application/json",
                    response_schema=RecommendationPlan,
                ),
            )

            if getattr(response, "parsed", None):
                plan = (
                    response.parsed
                    if isinstance(response.parsed, RecommendationPlan)
                    else RecommendationPlan.model_validate(response.parsed)
                )
            else:
                plan = RecommendationPlan.model_validate_json(response.text)

            return self._normalize_budget(plan, user_input)
        except Exception:
            return None

    @staticmethod
    def _normalize_budget(
        plan: RecommendationPlan,
        user_input: dict[str, Any],
    ) -> RecommendationPlan | None:
        budget = float(user_input["budget"])
        currency = str(user_input.get("currency", "INR")).upper()

        if not plan.recommendations:
            return None

        plan.total_budget = budget
        plan.currency = currency

        item_total = sum(
            item.estimated_price for item in plan.recommendations
        )

        if item_total > budget and item_total > 0:
            scale = budget / item_total
            for item in plan.recommendations:
                item.estimated_price = round(
                    item.estimated_price * scale,
                    2,
                )
            item_total = sum(
                item.estimated_price for item in plan.recommendations
            )

        plan.estimated_total = round(min(item_total, budget), 2)

        allocation_total = sum(item.amount for item in plan.allocations)
        if allocation_total > budget and allocation_total > 0:
            scale = budget / allocation_total
            for allocation in plan.allocations:
                allocation.amount = round(allocation.amount * scale, 2)
                allocation.percentage = round(
                    allocation.amount / budget * 100,
                    1,
                )

        return plan


gemini_service = GeminiService()
