from types import SimpleNamespace

from fastapi.testclient import TestClient

from meal_planner.config import Settings, get_settings
from meal_planner.main import app
from meal_planner.schemas import (
    CookSuggestion,
    CookSuggestions,
    CookRequest,
    Ingredient,
    Meal,
    MealPlan,
    MemberInput,
    PlanRequest,
    Portion,
    RecipeGuide,
    RecipeLookupRequest,
    RelatedRecipe,
)
from meal_planner.service import (
    _compact_payload,
    _fresh_cook_suggestions,
    find_recipe,
    generate_cook_suggestions,
    validate_plan,
)


def test_health_reports_missing_key() -> None:
    app.dependency_overrides[get_settings] = lambda: Settings(
        openai_api_key=None, openai_model="test-model"
    )
    client = TestClient(app)

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "api_key_configured": False,
        "default_model": "test-model",
    }
    app.dependency_overrides.clear()


def test_index_disables_cache_during_ui_testing() -> None:
    response = TestClient(app).get("/")

    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store, max-age=0"
    assert "Include prepare-ahead meals" in response.text


def test_generate_requires_api_key() -> None:
    app.dependency_overrides[get_settings] = lambda: Settings(openai_api_key=None)
    client = TestClient(app)

    response = client.post(
        "/api/generate-plan",
        json={"members": [{"name": "Adult 1"}], "meals": ["dinner"]},
    )

    assert response.status_code == 503
    app.dependency_overrides.clear()


def test_allergen_validation_detects_matching_ingredient() -> None:
    request = PlanRequest(
        members=[MemberInput(name="Sam", allergies=["peanut"])], meals=["dinner"]
    )
    plan = MealPlan(
        meals=[
            Meal(
                day="Today",
                meal_type="dinner",
                name="Noodles",
                prep_minutes=10,
                cook_minutes=10,
                ingredients=[
                    Ingredient(name="peanut butter", quantity="1 tbsp")
                ],
                missing_ingredients=[],
                steps=["Cook."],
                portions=[
                    Portion(
                        member="Sam",
                        description="1 bowl",
                        estimated_calories=500,
                        estimated_protein_g=25,
                    )
                ],
                reason_tags=[],
            )
        ],
    )

    result = validate_plan(plan, request)

    assert result.passed is False
    assert "peanut butter" in result.violations[0]
    assert result.warnings


def test_new_mvp_endpoints_require_api_key() -> None:
    app.dependency_overrides[get_settings] = lambda: Settings(openai_api_key=None)
    client = TestClient(app)

    rules = client.post(
        "/api/interpret-rules",
        json={"members": [{"name": "Adult 1"}], "instructions": "No rice."},
    )
    cook = client.post(
        "/api/cook",
        json={"members": [{"name": "Adult 1"}], "available_ingredients": ["rice"]},
    )
    recipe = client.post(
        "/api/find-recipe",
        json={"query": "raw mango sweet pickle"},
    )

    assert rules.status_code == 503
    assert cook.status_code == 503
    assert recipe.status_code == 503
    app.dependency_overrides.clear()


def test_pantry_staples_are_assumed_by_default() -> None:
    request = PlanRequest(members=[MemberInput(name="Adult 1")])

    assert request.assume_pantry_staples is True


def test_compact_payload_removes_blank_optional_values() -> None:
    compacted = _compact_payload(
        {
            "model": "gpt-6-luna",
            "developer_prompt": "custom",
            "instructions": "",
            "available_ingredients": [],
            "start_date": None,
            "assume_pantry_staples": False,
            "members": [{"name": "Adult 1", "allergies": []}],
        }
    )

    assert compacted == {
        "assume_pantry_staples": False,
        "members": [{"name": "Adult 1"}],
    }


def test_plan_validation_rejects_duplicate_meals_and_too_many_missing_items() -> None:
    request = PlanRequest(
        members=[MemberInput(name="Adult 1")],
        meals=["dinner"],
        max_missing_ingredients=1,
    )

    def meal(day: str) -> Meal:
        return Meal(
            day=day,
            meal_type="dinner",
            name="Vegetable pulao",
            prep_minutes=10,
            cook_minutes=20,
            ingredients=[Ingredient(name="rice", quantity="1 cup")],
            missing_ingredients=[
                Ingredient(name="peas", quantity="1 cup"),
                Ingredient(name="carrot", quantity="1"),
            ],
            steps=["Cook until the rice is tender."],
            portions=[],
            reason_tags=[],
        )

    result = validate_plan(MealPlan(meals=[meal("Monday"), meal("Tuesday")]), request)

    assert result.passed is False
    assert any("repeated" in violation for violation in result.violations)
    assert any("missing-ingredient" in violation for violation in result.violations)


def test_cook_load_more_removes_previous_and_same_batch_duplicates() -> None:
    def suggestion(name: str) -> CookSuggestion:
        return CookSuggestion(
            name=name,
            total_minutes=20,
            missing_ingredients=[],
            all_ingredients=[Ingredient(name="rice", quantity="1 cup")],
            steps=["Cook until tender."],
            portions=[],
            reason_tags=[],
        )

    result = _fresh_cook_suggestions(
        CookSuggestions(
            suggestions=[
                suggestion("Vegetable Pulao"),
                suggestion("Tomato Rice"),
                suggestion("tomato-rice"),
            ]
        ),
        ["vegetable pulao"],
    )

    assert [item.name for item in result.suggestions] == ["Tomato Rice"]


def test_cook_automatically_tops_up_a_short_first_result(monkeypatch) -> None:
    def suggestion(name: str) -> CookSuggestion:
        return CookSuggestion(
            name=name,
            total_minutes=25,
            missing_ingredients=[],
            all_ingredients=[Ingredient(name="soji", quantity="1 cup")],
            steps=["Cook until done."],
            portions=[],
            reason_tags=[],
        )

    batches = [
        CookSuggestions(suggestions=[suggestion("Upma")]),
        CookSuggestions(
            suggestions=[suggestion("Pesarattu"), suggestion("Urad Dal Vada")]
        ),
    ]
    inputs = []

    class FakeResponses:
        def parse(self, **kwargs):
            inputs.append(kwargs["input"])
            parsed = batches.pop(0)
            return SimpleNamespace(
                id=f"response-{len(inputs)}",
                model="test-model",
                output_parsed=parsed,
                usage=SimpleNamespace(
                    input_tokens=10, output_tokens=20, total_tokens=30
                ),
            )

    monkeypatch.setattr(
        "meal_planner.service.OpenAI",
        lambda api_key: SimpleNamespace(responses=FakeResponses()),
    )
    response = generate_cook_suggestions(
        CookRequest(
            members=[MemberInput(name="Adult 1")],
            available_ingredients=["mag ni dal", "urad ni dal", "soji"],
            instructions="Kaink aam South Indian nu nasto khavo che",
        ),
        Settings(openai_api_key="test-key", openai_model="test-model"),
    )

    assert [item.name for item in response.result.suggestions] == [
        "Upma",
        "Pesarattu",
        "Urad Dal Vada",
    ]
    assert len(inputs) == 2
    assert '"excluded_recipe_names":["Upma"]' in inputs[1]
    assert response.metadata.total_tokens == 60


def test_find_recipe_uses_description_and_optional_servings(monkeypatch) -> None:
    parsed = RecipeGuide(
        name="Raw Mango Sweet Pickle",
        summary="A sweet and tangy mango pickle.",
        servings=6,
        total_minutes=45,
        ingredients=[Ingredient(name="raw mango", quantity="2 cups")],
        steps=["Wash the mango and dry it fully."],
        tips=["Keep water out of the jar."],
        related_recipes=[
            RelatedRecipe(name="Mango Chutney", reason="Another sweet mango recipe.")
        ],
    )
    inputs = []

    class FakeResponses:
        def parse(self, **kwargs):
            inputs.append(kwargs["input"])
            return SimpleNamespace(
                id="recipe-response",
                model="test-model",
                output_parsed=parsed,
                usage=SimpleNamespace(
                    input_tokens=10, output_tokens=20, total_tokens=30
                ),
            )

    monkeypatch.setattr(
        "meal_planner.service.OpenAI",
        lambda api_key: SimpleNamespace(responses=FakeResponses()),
    )

    response = find_recipe(
        RecipeLookupRequest(query="raw mango sweet pickle", servings=6),
        Settings(openai_api_key="test-key", openai_model="test-model"),
    )

    assert response.recipe.name == "Raw Mango Sweet Pickle"
    assert response.recipe.servings == 6
    assert '"query":"raw mango sweet pickle"' in inputs[0]
    assert '"servings":6' in inputs[0]
