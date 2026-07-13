# Zomato Restaurant Recommendation System

An AI-powered restaurant recommendation service inspired by Zomato, combining structured dataset filtering with LLM-based ranking and explanation (using Groq).

## Milestone 1 Setup & Configuration

This project requires Python 3.10+ and a valid Groq API Key.

### Initial Setup

1. **Clone/scaffold the directory**:
   Ensure you are in the project root directory: `zomato-milestone1`.

2. **Set up a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Copy `.env.example` to `.env` and fill in your variables:
   ```bash
   cp .env.example .env
   ```
   Open `.env` and add your `GROQ_API_KEY`:
   ```env
   GROQ_API_KEY=gsk_...
   ```

### Running Tests

To verify that the configuration and components are set up correctly:
```bash
pytest tests/
```
