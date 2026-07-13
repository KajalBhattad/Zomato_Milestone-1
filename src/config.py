import os
# pyrefly: ignore [missing-import]
from pydantic import Field
# pyrefly: ignore [missing-import]
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Groq API Config
    groq_api_key: str = Field(default="", validation_alias="GROQ_API_KEY")
    groq_model: str = Field(default="llama-3.3-70b-versatile", validation_alias="GROQ_MODEL")
    groq_temperature: float = Field(default=0.3, validation_alias="GROQ_TEMPERATURE")

    # Dataset Config
    hf_dataset_name: str = Field(
        default="ManikaSaini/zomato-restaurant-recommendation",
        validation_alias="HF_DATASET_NAME"
    )
    local_parquet_path: str = Field(
        default="data/restaurants.parquet",
        validation_alias="LOCAL_PARQUET_PATH"
    )


    # Recommendation Config
    max_candidates: int = Field(default=30, validation_alias="MAX_CANDIDATES")
    top_k_results: int = Field(default=5, validation_alias="TOP_K_RESULTS")

    # Budget Tiers
    budget_low_max: int = Field(default=500, validation_alias="BUDGET_LOW_MAX")
    budget_medium_max: int = Field(default=1500, validation_alias="BUDGET_MEDIUM_MAX")

    model_config = SettingsConfigDict(
        # Load from .env file if it exists, otherwise fall back to environment variables
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def validate_api_key(self) -> None:
        """
        Validate that the GROQ_API_KEY is configured.
        Raises ValueError if the key is missing, empty, or set to placeholder value.
        """
        key = self.groq_api_key.strip() if self.groq_api_key else ""
        if not key or key == "your_groq_api_key_here":
            raise ValueError(
                "CRITICAL CONFIGURATION ERROR: GROQ_API_KEY is not set or is still the placeholder value. "
                "Please configure a valid GROQ_API_KEY in your .env file or system environment."
            )

# Create settings singleton instance
settings = Settings()
