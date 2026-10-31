# Family Meal Planner — API MVP

A deliberately small prompt lab for validating OpenAI API requests and structured meal-plan responses before building the product UI.

## Run locally

1. Copy the environment template and add your key:

   ```bash
   cp .env.example .env
   ```

2. Install and start with `uv`:

   ```bash
   uv sync
   uv run uvicorn meal_planner.main:app --reload
   ```

3. Open <http://127.0.0.1:8000>.

The API key stays in the Python process and is never sent to the browser. Change `OPENAI_MODEL` in `.env`, or override the model from the test UI.

## What this validates

- Python calls to the OpenAI Responses API
- Pydantic-backed Structured Outputs
- Editable developer prompts for fast prompt iteration
- Three focused test tabs: household/rules, daily or weekly plans, and cook-with-ingredients
- Structured daily and seven-day meal plans for a household
- Natural-language rule interpretation with conflicts and clarification questions
- Ranked ingredient-based meal suggestions
- Response ID, model, latency, and token usage
- A basic deterministic allergen string scan after generation

The allergen scan is intentionally conservative and is **not production-safe**. The PRD requires normalized recipe data, compound-ingredient handling, and a verified allergen pipeline before launch.

## API

- `GET /api/health` — app/API-key configuration status
- `GET /api/config` — default model and editable developer prompt
- `POST /api/generate-plan` — generate and validate a structured plan

Run tests with:

```bash
uv run pytest
```
