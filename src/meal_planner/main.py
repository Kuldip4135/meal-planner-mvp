from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from openai import APIConnectionError, APIStatusError, AuthenticationError, RateLimitError

from .config import Settings, get_settings
from .prompts import COOK_DEVELOPER_PROMPT, DEFAULT_DEVELOPER_PROMPT, RULE_INTERPRETER_PROMPT
from .schemas import (
    CookRequest,
    CookResponse,
    PlanRequest,
    PlanResponse,
    RecipeLookupRequest,
    RecipeLookupResponse,
    RuleInterpretRequest,
    RuleInterpretResponse,
)
from .service import find_recipe, generate_cook_suggestions, generate_plan, interpret_rules

app = FastAPI(title="Family Meal Planner API Lab", version="0.1.0")
STATIC_DIR = Path(__file__).parent / "static"


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(
        STATIC_DIR / "index.html",
        headers={"Cache-Control": "no-store, max-age=0"},
    )


@app.get("/api/health")
def health(settings: Settings = Depends(get_settings)) -> dict[str, object]:
    return {
        "status": "ok",
        "api_key_configured": bool(settings.openai_api_key),
        "default_model": settings.openai_model,
    }


@app.get("/api/config")
def config(settings: Settings = Depends(get_settings)) -> dict[str, str]:
    return {
        "default_model": settings.openai_model,
        "developer_prompt": DEFAULT_DEVELOPER_PROMPT,
        "rule_prompt": RULE_INTERPRETER_PROMPT,
        "cook_prompt": COOK_DEVELOPER_PROMPT,
    }


@app.post("/api/generate-plan", response_model=PlanResponse)
def create_plan(
    request: PlanRequest, settings: Settings = Depends(get_settings)
) -> PlanResponse:
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=503,
            detail="OPENAI_API_KEY is not configured. Copy .env.example to .env and add your key.",
        )
    try:
        return generate_plan(request, settings)
    except AuthenticationError as exc:
        raise HTTPException(status_code=401, detail="OpenAI rejected the API key.") from exc
    except RateLimitError as exc:
        raise HTTPException(
            status_code=429, detail="OpenAI rate or usage limit reached. Try again shortly."
        ) from exc
    except APIConnectionError as exc:
        raise HTTPException(status_code=502, detail="Could not connect to OpenAI.") from exc
    except APIStatusError as exc:
        raise HTTPException(
            status_code=502, detail=f"OpenAI API error ({exc.status_code}): {exc.message}"
        ) from exc


@app.post("/api/interpret-rules", response_model=RuleInterpretResponse)
def create_rule_interpretation(
    request: RuleInterpretRequest, settings: Settings = Depends(get_settings)
) -> RuleInterpretResponse:
    _require_key(settings)
    try:
        return interpret_rules(request, settings)
    except (AuthenticationError, RateLimitError, APIConnectionError, APIStatusError) as exc:
        _raise_openai_error(exc)


@app.post("/api/cook", response_model=CookResponse)
def create_cook_suggestions(
    request: CookRequest, settings: Settings = Depends(get_settings)
) -> CookResponse:
    _require_key(settings)
    try:
        return generate_cook_suggestions(request, settings)
    except (AuthenticationError, RateLimitError, APIConnectionError, APIStatusError) as exc:
        _raise_openai_error(exc)


@app.post("/api/find-recipe", response_model=RecipeLookupResponse)
def create_recipe_guide(
    request: RecipeLookupRequest, settings: Settings = Depends(get_settings)
) -> RecipeLookupResponse:
    _require_key(settings)
    try:
        return find_recipe(request, settings)
    except (AuthenticationError, RateLimitError, APIConnectionError, APIStatusError) as exc:
        _raise_openai_error(exc)


def _require_key(settings: Settings) -> None:
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=503,
            detail="OPENAI_API_KEY is not configured. Copy .env.example to .env and add your key.",
        )


def _raise_openai_error(exc) -> None:
    if isinstance(exc, AuthenticationError):
        raise HTTPException(status_code=401, detail="OpenAI rejected the API key.") from exc
    if isinstance(exc, RateLimitError):
        raise HTTPException(status_code=429, detail="OpenAI rate or usage limit reached.") from exc
    if isinstance(exc, APIConnectionError):
        raise HTTPException(status_code=502, detail="Could not connect to OpenAI.") from exc
    raise HTTPException(status_code=502, detail=f"OpenAI API error ({exc.status_code}): {exc.message}") from exc
