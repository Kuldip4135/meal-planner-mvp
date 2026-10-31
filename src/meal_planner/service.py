import json
import re
from time import perf_counter

from openai import OpenAI

from .config import Settings
from .prompts import (
    COOK_DEVELOPER_PROMPT,
    DEFAULT_DEVELOPER_PROMPT,
    RECIPE_LOOKUP_PROMPT,
    RULE_INTERPRETER_PROMPT,
)
from .schemas import (
    ApiMetadata,
    CookRequest,
    CookResponse,
    CookSuggestions,
    MealPlan,
    PlanRequest,
    PlanResponse,
    RecipeGuide,
    RecipeLookupRequest,
    RecipeLookupResponse,
    RuleInterpretRequest,
    RuleInterpretation,
    RuleInterpretResponse,
    ValidationResult,
)

PANTRY_STAPLES = {
    "water",
    "salt",
    "black pepper",
    "pepper",
    "neutral oil",
    "cooking oil",
    "vegetable oil",
    "cumin",
    "coriander powder",
    "turmeric",
    "chili powder",
    "paprika",
    "oregano",
    "thyme",
    "cinnamon",
    "garam masala",
}

def _compact_payload(value):
    """Remove blank optional values before they consume input tokens."""
    if isinstance(value, dict):
        compacted = {
            key: _compact_payload(item)
            for key, item in value.items()
            if key not in {"model", "developer_prompt"}
        }
        return {
            key: item
            for key, item in compacted.items()
            if item not in (None, "", [], {})
        }
    if isinstance(value, list):
        return [_compact_payload(item) for item in value]
    return value


def _request_payload(request: PlanRequest) -> str:
    payload = _compact_payload(request.model_dump())
    day_count = 7 if request.plan_length == "seven_days" else 1
    meal_count = day_count * len(request.meals)
    return (
        f"Create a {day_count}-day household meal plan with exactly {meal_count} meals: "
        f"one meal for each requested meal type on each day. Interpret the household's "
        "natural-language preferences within the developer constraints.\n\n"
        + json.dumps(payload, separators=(",", ":"))
    )


def validate_plan(plan: MealPlan, request: PlanRequest) -> ValidationResult:
    violations: list[str] = []
    warnings: list[str] = []
    ingredient_rows = [
        (meal.name, ingredient)
        for meal in plan.meals
        for ingredient in meal.ingredients
    ]

    for member in request.members:
        for allergen in member.allergies:
            token = allergen.strip().casefold()
            if not token:
                continue
            matcher = re.compile(rf"\b{re.escape(token)}\b", re.IGNORECASE)
            for meal_name, ingredient in ingredient_rows:
                if matcher.search(ingredient.name):
                    violations.append(
                        f"{meal_name}: ingredient '{ingredient.name}' may contain "
                        f"{member.name}'s allergen '{allergen}'."
                    )

    seen_meals: set[str] = set()
    for meal in plan.meals:
        normalized_name = re.sub(r"[^a-z0-9]+", " ", meal.name.casefold()).strip()
        if normalized_name in seen_meals:
            violations.append(f"{meal.name}: this recipe is repeated in the plan.")
        seen_meals.add(normalized_name)

        counted_missing = [
            ingredient
            for ingredient in meal.missing_ingredients
            if not (
                request.assume_pantry_staples
                and ingredient.name.strip().casefold() in PANTRY_STAPLES
            )
        ]
        if len(counted_missing) > request.max_missing_ingredients:
            violations.append(
                f"{meal.name}: exceeds the missing-ingredient allowance."
            )
        if not request.allow_advance_prep and not meal.ready_now:
            violations.append(f"{meal.name}: requires advance preparation.")
        if not meal.ready_now and not meal.advance_prep_note:
            violations.append(f"{meal.name}: is missing advance-preparation guidance.")

    warnings.append(
        "Before cooking, check that every ingredient is fresh, safe to eat, and not expired, spoiled, or rotten."
    )
    return ValidationResult(
        passed=not violations, violations=violations, warnings=warnings
    )


def generate_plan(request: PlanRequest, settings: Settings) -> PlanResponse:
    model = request.model or settings.openai_model
    prompt = request.developer_prompt or DEFAULT_DEVELOPER_PROMPT
    client = OpenAI(api_key=settings.openai_api_key)
    started = perf_counter()
    response = client.responses.parse(
        model=model,
        instructions=prompt,
        input=_request_payload(request),
        reasoning={"effort": "low"},
        text_format=MealPlan,
    )
    latency_ms = round((perf_counter() - started) * 1000)

    if response.output_parsed is None:
        raise RuntimeError("The model returned no structured meal plan.")

    usage = response.usage
    metadata = ApiMetadata(
        response_id=response.id,
        model=response.model,
        latency_ms=latency_ms,
        input_tokens=getattr(usage, "input_tokens", None),
        output_tokens=getattr(usage, "output_tokens", None),
        total_tokens=getattr(usage, "total_tokens", None),
    )
    return PlanResponse(
        plan=response.output_parsed,
        validation=validate_plan(response.output_parsed, request),
        metadata=metadata,
    )


def _metadata(response, started: float) -> ApiMetadata:
    usage = response.usage
    return ApiMetadata(
        response_id=response.id,
        model=response.model,
        latency_ms=round((perf_counter() - started) * 1000),
        input_tokens=getattr(usage, "input_tokens", None),
        output_tokens=getattr(usage, "output_tokens", None),
        total_tokens=getattr(usage, "total_tokens", None),
    )


def _combined_metadata(responses: list, started: float) -> ApiMetadata:
    """Report complete usage when a short result requires one automatic top-up."""
    latest = responses[-1]

    def total(field: str):
        values = [getattr(response.usage, field, None) for response in responses]
        return sum(value for value in values if value is not None) if any(
            value is not None for value in values
        ) else None

    return ApiMetadata(
        response_id=latest.id,
        model=latest.model,
        latency_ms=round((perf_counter() - started) * 1000),
        input_tokens=total("input_tokens"),
        output_tokens=total("output_tokens"),
        total_tokens=total("total_tokens"),
    )


def interpret_rules(request: RuleInterpretRequest, settings: Settings) -> RuleInterpretResponse:
    client = OpenAI(api_key=settings.openai_api_key)
    started = perf_counter()
    response = client.responses.parse(
        model=request.model or settings.openai_model,
        instructions=request.developer_prompt or RULE_INTERPRETER_PROMPT,
        input=json.dumps(_compact_payload(request.model_dump()), separators=(",", ":")),
        reasoning={"effort": "low"},
        text_format=RuleInterpretation,
    )
    if response.output_parsed is None:
        raise RuntimeError("The model returned no structured rule interpretation.")
    return RuleInterpretResponse(
        interpretation=response.output_parsed,
        metadata=_metadata(response, started),
    )


def validate_cook(result: CookSuggestions, request: CookRequest) -> ValidationResult:
    plan = MealPlan(
        meals=[
            {
                "day": "Cook now",
                "meal_type": "dinner",
                "name": suggestion.name,
                "prep_minutes": 0,
                "cook_minutes": suggestion.total_minutes,
                "ingredients": suggestion.all_ingredients,
                "missing_ingredients": suggestion.missing_ingredients,
                "steps": suggestion.steps,
                "portions": suggestion.portions,
                "reason_tags": suggestion.reason_tags,
            }
            for suggestion in result.suggestions
        ],
    )
    proxy = PlanRequest(
        members=request.members or [{"name": "Cook"}],
        meals=["dinner"],
        assume_pantry_staples=request.assume_pantry_staples,
        max_missing_ingredients=request.max_missing_ingredients,
        allow_advance_prep=request.allow_advance_prep,
    )
    validation = validate_plan(plan, proxy)
    for suggestion in result.suggestions:
        if suggestion.total_minutes > request.max_minutes:
            validation.violations.append(f"{suggestion.name}: exceeds the time limit.")
    validation.passed = not validation.violations
    return validation


def _fresh_cook_suggestions(
    result: CookSuggestions, excluded_recipe_names: list[str]
) -> CookSuggestions:
    """Remove exact normalized duplicates from previous and current result batches."""
    seen = {
        re.sub(r"[^a-z0-9]+", " ", name.casefold()).strip()
        for name in excluded_recipe_names
    }
    fresh = []
    for suggestion in result.suggestions:
        normalized = re.sub(r"[^a-z0-9]+", " ", suggestion.name.casefold()).strip()
        if normalized in seen:
            continue
        seen.add(normalized)
        fresh.append(suggestion)
    return CookSuggestions(suggestions=fresh)


def generate_cook_suggestions(request: CookRequest, settings: Settings) -> CookResponse:
    client = OpenAI(api_key=settings.openai_api_key)
    started = perf_counter()
    model = request.model or settings.openai_model
    instructions = request.developer_prompt or COOK_DEVELOPER_PROMPT

    def request_batch(batch_request: CookRequest, count: int):
        return client.responses.parse(
            model=model,
            instructions=instructions,
            input=(
                f"Return exactly {count} new ranked meal suggestion"
                f"{'s' if count != 1 else ''} from this household JSON. "
                "Use all culinary context, including regional-language transliteration. "
                "Return fewer only if safety or hard constraints make the requested count impossible.\n\n"
                + json.dumps(
                    _compact_payload(batch_request.model_dump()), separators=(",", ":")
                )
            ),
            reasoning={"effort": "low"},
            text_format=CookSuggestions,
        )

    response = request_batch(request, 3)
    responses = [response]
    if response.output_parsed is None:
        raise RuntimeError("The model returned no structured cooking suggestions.")
    result = _fresh_cook_suggestions(
        response.output_parsed, request.excluded_recipe_names
    )
    if len(result.suggestions) < 3:
        shown_names = request.excluded_recipe_names + [
            suggestion.name for suggestion in result.suggestions
        ]
        retry_request = request.model_copy(
            update={"excluded_recipe_names": shown_names}
        )
        response = request_batch(retry_request, 3 - len(result.suggestions))
        responses.append(response)
        if response.output_parsed is not None:
            extra = _fresh_cook_suggestions(response.output_parsed, shown_names)
            result = CookSuggestions(
                suggestions=(result.suggestions + extra.suggestions)[:3]
            )
    return CookResponse(
        result=result,
        validation=validate_cook(result, request),
        metadata=_combined_metadata(responses, started),
    )


def find_recipe(request: RecipeLookupRequest, settings: Settings) -> RecipeLookupResponse:
    client = OpenAI(api_key=settings.openai_api_key)
    started = perf_counter()
    response = client.responses.parse(
        model=request.model or settings.openai_model,
        instructions=request.developer_prompt or RECIPE_LOOKUP_PROMPT,
        input=json.dumps(_compact_payload(request.model_dump()), separators=(",", ":")),
        reasoning={"effort": "low"},
        text_format=RecipeGuide,
    )
    if response.output_parsed is None:
        raise RuntimeError("The model returned no recipe guide.")
    return RecipeLookupResponse(
        recipe=response.output_parsed,
        metadata=_metadata(response, started),
    )
