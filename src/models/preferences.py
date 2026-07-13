from typing import Literal, Optional
# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field, field_validator

class UserPreferences(BaseModel):
    location: str = Field(description="Target location for recommendations (required)")
    budget: Literal["low", "medium", "high"] = Field(description="Budget tier (required: low, medium, high)")
    cuisine: Optional[str] = Field(default=None, description="Optional cuisine filter (e.g., Italian, Chinese)")
    min_rating: float = Field(default=0.0, description="Minimum restaurant rating threshold (0.0 to 5.0)")
    additional_preferences: Optional[str] = Field(
        default=None,
        description="Optional additional preferences (max 200 chars)"
    )

    @field_validator("location")
    @classmethod
    def validate_location(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("location must be a non-empty string.")
        return trimmed

    @field_validator("min_rating")
    @classmethod
    def validate_min_rating(cls, value: float) -> float:
        if not (0.0 <= value <= 5.0):
            raise ValueError("min_rating must be between 0.0 and 5.0.")
        return value

    @field_validator("additional_preferences")
    @classmethod
    def validate_additional_preferences(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        trimmed = value.strip()
        # Sanitize length to mitigate prompt injection and token overflow risks
        if len(trimmed) > 200:
            trimmed = trimmed[:200]
        return trimmed
