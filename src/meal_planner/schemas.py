from typing import Literal

from pydantic import BaseModel, Field, field_validator


class MemberInput(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    kind: Literal["adult", "child"] = "adult"
    allergies: list[str] = Field(default_factory=list)
    avoidances: list[str] = Field(default_factory=list)
    min_protein_g: int | None = Field(default=None, ge=0, le=150)
    min_calories: int | None = Field(default=None, ge=0, le=2000)
    max_calories: int | None = Field(default=None, ge=0, le=2500)

    @field_validator("max_calories")
    @classmethod
    def calories_are_ordered(cls, value: int | None, info):
        minimum = info.data.get("min_calories")
        if value is not None and minimum is not None and value < minimum:
            raise ValueError("max_calories must be greater than or equal to min_calories")
        return value


class PlanRequest(BaseModel):
    members: list[MemberInput] = Field(min_length=1, max_length=12)
    instructions: str = Field(default="", max_length=3000)
    plan_notes: str = Field(default="", max_length=3000)
    available_ingredients: list[str] = Field(default_factory=list, max_length=60)
    meals: list[Literal["breakfast", "lunch", "dinner"]] = Field(
        default_factory=lambda: ["breakfast", "lunch", "dinner"], min_length=1
    )
    plan_length: Literal["today", "seven_days"] = "today"
    start_date: str | None = Field(default=None, max_length=20)
    assume_pantry_staples: bool = True
    allow_advance_prep: bool = True
    max_missing_ingredients: int = Field(default=2, ge=0, le=10)
    model: str | None = Field(default=None, max_length=100)
    developer_prompt: str | None = Field(default=None, max_length=12000)


class InterpretedRule(BaseModel):
    summary: str = Field(description="Short confirmation chip shown to the user")
    priority: int = Field(ge=1, le=7)
    needs_clarification: bool


class RuleInterpretRequest(BaseModel):
    members: list[MemberInput] = Field(min_length=1, max_length=12)
    instructions: str = Field(min_length=1, max_length=3000)
    model: str | None = Field(default=None, max_length=100)
    developer_prompt: str | None = Field(default=None, max_length=12000)


class RuleInterpretation(BaseModel):
    rules: list[InterpretedRule]
    conflicts: list[str]
    clarification_questions: list[str]


class Portion(BaseModel):
    member: str
    description: str
    estimated_calories: int = Field(ge=0)
    estimated_protein_g: int = Field(ge=0)


class Ingredient(BaseModel):
    name: str
    quantity: str


class Meal(BaseModel):
    day: str = Field(description="ISO date or clear day label")
    meal_type: Literal["breakfast", "lunch", "dinner"]
    name: str
    prep_minutes: int = Field(ge=0, le=600)
    cook_minutes: int = Field(ge=0, le=600)
    advance_prep_minutes: int = Field(default=0, ge=0, le=10080)
    advance_prep_note: str = Field(default="", max_length=300)
    ready_now: bool = True
    cooking_method: str = Field(default="", max_length=80)
    ingredients: list[Ingredient] = Field(min_length=1)
    missing_ingredients: list[Ingredient]
    steps: list[str] = Field(
        min_length=1,
        description=(
            "Complete ordered cooking steps in simple everyday language, with one clear "
            "action per step, useful timing, and an easy-to-understand sign that it is ready"
        ),
    )
    portions: list[Portion]
    reason_tags: list[str]


class MealPlan(BaseModel):
    meals: list[Meal]


class ValidationResult(BaseModel):
    passed: bool
    violations: list[str]
    warnings: list[str]


class ApiMetadata(BaseModel):
    response_id: str
    model: str
    latency_ms: int
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None


class PlanResponse(BaseModel):
    plan: MealPlan
    validation: ValidationResult
    metadata: ApiMetadata


class RuleInterpretResponse(BaseModel):
    interpretation: RuleInterpretation
    metadata: ApiMetadata


class CookRequest(BaseModel):
    members: list[MemberInput] = Field(default_factory=list, max_length=12)
    available_ingredients: list[str] = Field(min_length=1, max_length=60)
    max_missing_ingredients: int = Field(default=2, ge=0, le=10)
    max_minutes: int = Field(default=30, ge=5, le=240)
    assume_pantry_staples: bool = True
    allow_advance_prep: bool = True
    instructions: str = Field(default="", max_length=3000)
    excluded_recipe_names: list[str] = Field(default_factory=list, max_length=60)
    model: str | None = Field(default=None, max_length=100)
    developer_prompt: str | None = Field(default=None, max_length=12000)


class CookSuggestion(BaseModel):
    name: str
    total_minutes: int = Field(
        ge=0, le=600, description="Active preparation and cooking time"
    )
    advance_prep_minutes: int = Field(default=0, ge=0, le=10080)
    advance_prep_note: str = Field(default="", max_length=300)
    ready_now: bool = True
    cooking_method: str = Field(default="", max_length=80)
    missing_ingredients: list[Ingredient]
    all_ingredients: list[Ingredient] = Field(min_length=1)
    steps: list[str] = Field(
        min_length=1,
        description=(
            "Complete ordered cooking steps in simple everyday language, with one clear "
            "action per step, useful timing, and an easy-to-understand sign that it is ready"
        ),
    )
    portions: list[Portion]
    reason_tags: list[str]


class CookSuggestions(BaseModel):
    suggestions: list[CookSuggestion]


class CookResponse(BaseModel):
    result: CookSuggestions
    validation: ValidationResult
    metadata: ApiMetadata


class RecipeLookupRequest(BaseModel):
    query: str = Field(min_length=2, max_length=500)
    servings: int | None = Field(default=None, ge=1, le=30)
    model: str | None = Field(default=None, max_length=100)
    developer_prompt: str | None = Field(default=None, max_length=12000)


class RelatedRecipe(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    reason: str = Field(min_length=1, max_length=240)


class RecipeGuide(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    summary: str = Field(min_length=1, max_length=500)
    servings: int = Field(ge=1, le=30)
    total_minutes: int = Field(ge=0, le=10080)
    ingredients: list[Ingredient] = Field(min_length=1)
    steps: list[str] = Field(
        min_length=1,
        description=(
            "Complete ordered cooking steps in simple everyday language, with one clear "
            "action per step, useful timing, and an easy-to-understand sign that it is ready"
        ),
    )
    tips: list[str] = Field(default_factory=list, max_length=8)
    related_recipes: list[RelatedRecipe] = Field(default_factory=list, max_length=3)


class RecipeLookupResponse(BaseModel):
    recipe: RecipeGuide
    metadata: ApiMetadata
