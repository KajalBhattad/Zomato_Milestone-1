# Project Context: AI-Powered Restaurant Recommendation System

> Source: [ProblemStatement.txt](./ProblemStatement.txt)

## Overview

Build an **AI-powered restaurant recommendation service** inspired by Zomato. The system intelligently suggests restaurants based on user preferences by combining **structured data** with a **Large Language Model (LLM)**.

## Objective

Design and implement an application that:

- Takes user preferences (location, budget, cuisine, ratings, etc.)
- Uses a real-world dataset of restaurants
- Leverages an LLM to generate personalized, human-like recommendations
- Displays clear and useful results to the user

## System Workflow

### 1. Data Ingestion

- Load and preprocess the Zomato dataset from Hugging Face
- **Dataset URL:** https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation
- Extract relevant fields such as:
  - Restaurant name
  - Location
  - Cuisine
  - Cost
  - Rating
  - (and other applicable fields from the dataset)

### 2. User Input

Collect user preferences:

| Preference | Examples |
|------------|----------|
| **Location** | Delhi, Bangalore |
| **Budget** | low, medium, high |
| **Cuisine** | Italian, Chinese |
| **Minimum rating** | Numeric threshold |
| **Additional preferences** | family-friendly, quick service, etc. |

### 3. Integration Layer

- Filter and prepare relevant restaurant data based on user input
- Pass structured results into an LLM prompt
- Design a prompt that helps the LLM reason and rank options

### 4. Recommendation Engine

Use the LLM to:

- **Rank** restaurants
- **Explain** why each recommendation fits the user's preferences
- **Optionally summarize** the overall set of choices

### 5. Output Display

Present top recommendations in a user-friendly format. Each recommendation should include:

- Restaurant Name
- Cuisine
- Rating
- Estimated Cost
- AI-generated explanation

## Key Technical Components

```
User Preferences → Data Filtering → LLM Prompt → Ranked Recommendations → UI Output
        ↑                    ↑
   Zomato Dataset (Hugging Face)
```

## Data Source

- **Platform:** Hugging Face
- **Dataset:** `ManikaSaini/zomato-restaurant-recommendation`
- **Link:** https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation

## Success Criteria

1. User can specify location, budget, cuisine, minimum rating, and optional preferences
2. System filters the Zomato dataset according to those inputs
3. Filtered data is fed to an LLM with a well-designed prompt
4. LLM returns ranked recommendations with human-readable explanations
5. Results are displayed clearly with name, cuisine, rating, cost, and explanation

## Scope Notes

- This is a **Zomato-inspired** use case (not a production Zomato integration)
- The LLM is central to ranking and explanation—not just a passthrough
- Structured filtering happens **before** the LLM call to keep prompts focused and efficient
