from typing import List, Optional
from pydantic import BaseModel, Field

class Recommendation(BaseModel):
    rank: int = Field(description="Recommendation rank (1 to TOP_K)")
    restaurant_name: str = Field(description="Name of the restaurant")
    cuisine: str = Field(description="Cuisine(s) formatted as string")
    rating: Optional[float] = Field(default=None, description="Numeric rating of the restaurant (None if unrated)")
    estimated_cost: str = Field(description="Formatted estimated cost (e.g. '₹800 for two')")
    explanation: str = Field(description="AI-generated explanation of why this restaurant fits the preferences")

class RecommendationResponse(BaseModel):
    summary: Optional[str] = Field(
        default=None,
        description="Optional AI-generated summary of the recommended choices"
    )
    recommendations: List[Recommendation] = Field(
        default_factory=list,
        description="List of ranked restaurant recommendations"
    )
