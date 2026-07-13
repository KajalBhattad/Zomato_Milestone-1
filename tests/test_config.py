# pyrefly: ignore [missing-import]
import pytest
from src.config import Settings

def test_default_settings():
    # Test that default settings loaded match what's expected
    settings = Settings()
    assert settings.groq_model == "llama-3.3-70b-versatile"
    assert settings.hf_dataset_name == "ManikaSaini/zomato-restaurant-recommendation"
    assert settings.max_candidates == 30
    assert settings.top_k_results == 5
    assert settings.budget_low_max == 500
    assert settings.budget_medium_max == 1500

def test_api_key_validation_fails_on_placeholder():
    settings = Settings(GROQ_API_KEY="your_groq_api_key_here")
    with pytest.raises(ValueError) as excinfo:
        settings.validate_api_key()
    assert "GROQ_API_KEY is not set" in str(excinfo.value)

def test_api_key_validation_fails_on_empty():
    settings = Settings(GROQ_API_KEY="   ")
    with pytest.raises(ValueError) as excinfo:
        settings.validate_api_key()
    assert "GROQ_API_KEY is not set" in str(excinfo.value)

def test_api_key_validation_passes_on_valid_key():
    settings = Settings(GROQ_API_KEY="gsk_somekeyval")
    # Should not raise any error
    settings.validate_api_key()
