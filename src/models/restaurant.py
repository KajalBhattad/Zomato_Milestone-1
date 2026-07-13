from typing import Any, Dict, List, Optional
# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field

class Restaurant(BaseModel):
    id: str = Field(description="Unique identifier for the restaurant")
    name: str = Field(description="Name of the restaurant")
    location: str = Field(description="Normalized location/city area")
    cuisines: List[str] = Field(default_factory=list, description="List of cuisines offered")
    rating: Optional[float] = Field(default=None, description="Restaurant rating out of 5 (None if unrated)")
    rating_text: str = Field(default="Unrated", description="Display text for rating, e.g., '4.1', 'NEW', 'Unrated'")
    cost_for_two: Optional[int] = Field(default=None, description="Estimated cost for two people in INR")
    budget_tier: str = Field(description="Budget tier: low, medium, or high")
    raw: Optional[Dict[str, Any]] = Field(default=None, description="Original raw record for debugging")

