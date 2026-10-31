# Product Requirements Document: Family Meal Planner for iOS

**Document status:** Draft for product and engineering planning  
**Platform:** iOS first  
**Version:** 1.0  
**Date:** October 18, 2026  
**Working product name:** Family Meal Planner

---

## 1. Product summary

Family Meal Planner creates practical daily or weekly meal plans for a household using four types of information:

1. Who is eating
2. Allergies, intolerances, and ingredients to avoid
3. Minimum calorie or protein requirements
4. Flexible instructions such as “paneer is allowed at lunch but not dinner”

It also answers a second frequent question: **“What can I cook with the ingredients I have?”**

The product is not intended to be a social recipe network, full calorie diary, fitness tracker, or complex pantry-management system. Its primary value is removing the mental work of deciding what a household can realistically eat.

### Core promise

> Tell us who is eating, what to avoid, and what each meal must achieve. Receive a practical family meal plan in under two minutes.

### Primary success moment

A new user completes household setup, generates a valid meal plan, and sees meals that visibly respect their household rules without needing to manually correct every result.

---

## 2. Problem statement

Household meal planning becomes difficult when family members have different:

- Allergies and intolerances
- Food dislikes
- Calorie or protein requirements
- Meal schedules
- Time-of-day restrictions
- Portion requirements
- Cultural or dietary preferences

Existing products commonly solve only one part of this problem. Some generate meals around calories, some store recipes, and others build shopping lists. Users still have to reconcile household restrictions, portions, available ingredients, and schedules manually.

The product must combine these constraints without making setup more complicated than planning meals manually.

---

## 3. Product goals

### 3.1 Launch goals

- Generate a useful daily or seven-day household meal plan.
- Respect allergies as hard safety constraints.
- Support household-wide rules and individual member exceptions.
- Satisfy optional per-meal calorie and protein requirements.
- Interpret additional natural-language instructions.
- Prefer one shared family meal with adjusted portions or safe substitutions.
- Let users replace unsuitable meals without regenerating the entire plan.
- Suggest meals from ingredients already available.
- Convert an accepted weekly plan into a simple consolidated shopping list.
- Become faster and more relevant through lightweight feedback.

### 3.2 Experience goals

- First plan generated in less than two minutes for most users.
- No account required before the user experiences the first generated plan.
- No more than four setup stages before first generation.
- Returning users can start generation from the Home screen in one tap.
- Every generated meal clearly explains how it satisfies the user's important rules.
- Important actions are reachable with one hand and use familiar iOS patterns.

### 3.3 Non-goals for launch

- Complete calorie or food-consumption diary
- Exercise, weight, or fitness tracking
- Social feed, followers, likes, or public profiles
- Grocery ordering or delivery integration
- Live supermarket pricing
- Full pantry inventory and automatic stock deduction
- Meal-photo calorie estimation
- Public recipe marketplace
- Diet diagnosis or medical advice

---

## 4. Target users

### 4.1 Primary audience

The primary user is the person responsible for planning or cooking meals for a household of two or more people. They have limited time and must regularly account for different needs.

Typical situations include:

- Parents planning meals for adults and children
- A household with one or more food allergies
- Families balancing different calorie or protein requirements
- Couples with different dietary preferences
- Households following recurring rules, such as vegetarian days
- Users who want to use available ingredients before buying more

### 4.2 Jobs to be done

When planning for my household, I want to enter everyone's important rules once so that I can receive meals everyone can eat without repeating those requirements.

When I need a plan, I want to generate today or the entire week quickly so that planning does not become another administrative task.

When a suggested meal is unsuitable, I want to replace only that meal so that I do not lose the rest of a good plan.

When I have ingredients at home, I want to see what I can cook now so that I waste less food and avoid unnecessary shopping.

---

## 5. Product principles

### 5.1 Constraints before recipes

The system must determine what is permitted before ranking what looks appealing. Allergies and explicit exclusions are never treated as optional preferences.

### 5.2 One household meal whenever practical

The app should first attempt to provide one shared base meal. It can vary portions and offer a safe substitution for an individual member. It should avoid recommending several unrelated recipes that increase cooking work.

### 5.3 Progressive disclosure

Show the simplest useful control first. Advanced nutrition values, member-specific exceptions, and rule details should appear only when requested.

### 5.4 Generate, explain, and allow correction

Every recommendation should have a concise reason. Every plan should be easy to correct using Swap, Lock, or Edit Rules.

### 5.5 Honest limitations

If requirements conflict, the system must explain the conflict instead of silently violating a rule or inventing inaccurate nutrition data.

### 5.6 Trust is more important than novelty

Reliable constraints, quantities, nutrition estimates, and shopping lists are more valuable than decorative AI features.

---

## 6. Information architecture

The launch app uses a four-item bottom tab bar:

1. **Home** — starting point, active plan, and primary actions
2. **Plan** — daily or weekly plan and meal details
3. **Cook** — “Cook with what I have” ingredient search
4. **List** — consolidated shopping list

Household settings are opened from the profile button in the top-right corner of Home. Settings should not occupy a permanent tab because they are configured infrequently.

### 6.1 Home structure

The Home screen presents three primary actions in this order:

1. Plan today
2. Plan my week
3. Cook with what I have

If a current plan exists, its next meal is shown above or immediately below these actions, depending on time relevance.

### 6.2 Navigation rules

- Use native iOS tab navigation for the four main destinations.
- Use sheets for short, reversible tasks such as swapping a meal or entering ingredients.
- Use full-screen flows for household setup and plan generation.
- Preserve user input if a sheet is dismissed accidentally.
- Avoid nested navigation deeper than three levels.
- Always provide a clear Back, Cancel, or Done action.
- Do not hide essential actions exclusively behind swipe gestures.

---

## 7. Core user journeys

## 7.1 First-use journey

```text
Welcome
  → Household size
  → Safety and avoidance rules
  → Nutrition requirements
  → Additional instructions and plan type
  → Confirm understood rules
  → Generate plan
  → Review plan
  → Accept plan
  → Shopping list
```

Account creation may be offered after the first plan is produced, with a clear value statement such as syncing and backup. It must be skippable at launch.

## 7.2 Returning-user journey

```text
Home
  → Plan today or Plan my week
  → Review existing rules
  → Generate
  → Swap or lock if needed
  → Accept
```

The saved household rules apply automatically. The user should not repeat onboarding.

## 7.3 Cook-with-ingredients journey

```text
Home or Cook tab
  → Enter or speak ingredients
  → Select missing-ingredient allowance and time
  → View ranked results
  → Open recipe
  → Start cooking or add missing items to List
```

---

## 8. Feature requirements

## 8.1 Household setup

### Purpose

Capture only the information required to generate valid household meals.

### Entry screen

Ask: **“How many people are eating?”**

- Stepper supporting 1–12 members
- Default value: 2
- Option: “Everyone follows the same rules”
- Option: “Set different rules for some people”

If individual rules are selected, create default labels such as Adult 1 and Member 2. Names are optional and editable later.

### Member information

For launch, collect only:

- Display name or default label
- Adult or child classification
- Allergy exceptions
- Avoidance exceptions
- Optional calorie range per meal
- Optional minimum protein per meal

Do not require date of birth, weight, height, biological sex, or activity level. The app accepts targets supplied by the user; it does not prescribe medical targets.

### Acceptance criteria

- A household can be created without making an account.
- A user can apply one rule to everyone or selected members.
- Member rules remain editable from Household Settings.
- Removing a member requires confirmation because it affects active plans.

---

## 8.2 Allergies, intolerances, and avoidances

### Purpose

Separate safety-critical exclusions from preferences.

### Categories

#### Allergies — hard constraint

Common chips should include:

- Milk
- Egg
- Fish
- Crustacean shellfish
- Tree nuts
- Peanuts
- Wheat
- Soy
- Sesame
- Custom allergen

#### Intolerances — exclude or substitute

Examples:

- Lactose
- Gluten
- Other custom intolerance

#### Avoid or dislike — ranking constraint

Examples:

- Spicy food
- Onion
- Garlic
- Mushroom
- Custom ingredient

### Interaction model

- Selecting an item opens a small selector: Everyone or specific members.
- Allergy selections use a visually distinct warning treatment, not only color.
- The user can search and add a custom item.
- The app clearly explains that it cannot guarantee absence of cross-contact or undeclared packaged-food ingredients.

### Generation behavior

- A meal containing a declared allergen for any selected eater must not be generated for that eater.
- The system may recommend a shared base meal with a verified alternative ingredient.
- Unknown compound ingredients, such as an unspecified sauce, must be flagged rather than assumed safe.
- AI-generated substitutions must be revalidated against all member rules.

### Acceptance criteria

- Allergy constraints cannot be weakened automatically.
- If no safe meal can be produced, generation stops and explains which rules caused the conflict.
- Every recipe shows a “Check packaged ingredients” notice when relevant.

---

## 8.3 Nutrition requirements

### Purpose

Allow users with known minimum requirements to constrain meals without forcing everyone into detailed macro tracking.

### Default interface

Ask: **“Does each meal need to meet a target?”**

Protein options:

- No target
- At least 20 g
- At least 30 g
- At least 40 g
- Custom

Calorie options:

- No target
- 300–500 kcal
- 500–700 kcal
- Custom range

Targets can be household-wide or member-specific.

### Rules

- Nutrition is shown as an estimate.
- The system must display calories and protein per recommended portion, not only for the entire recipe.
- A meal below a hard minimum cannot be labeled as satisfying the target.
- If only a near match exists, the app must request permission to show close alternatives.

### Acceptance criteria

- Users can skip nutrition targets entirely.
- Custom values are validated against reasonable numeric bounds.
- Portion calculations update when the number of eaters changes.

---

## 8.4 Natural-language instructions

### Purpose

Capture scheduling and food rules that would otherwise require a complicated settings interface.

### Input

Provide a text field with dictation support and example prompts:

- “Paneer is allowed at lunch but not dinner.”
- “Friday dinner must be vegetarian.”
- “Include spinach twice this week.”
- “Tuesday meals must take less than 20 minutes.”
- “Do not serve rice on consecutive days.”

### Interpretation flow

Before generation, convert input into short rule chips:

```text
Understood
• Exclude paneer from dinner
• Friday dinner is vegetarian
• Include spinach at least twice this week
```

The user can edit or remove any interpreted rule.

### Rule priority

1. Allergy safety
2. Explicit “must not” instructions
3. Explicit nutrition minimums
4. Explicit “must include” instructions
5. Time, equipment, and schedule constraints
6. Avoidances and dislikes
7. Variety and recommendation preferences

If rules at the same priority conflict, generation pauses and requests a correction.

### Acceptance criteria

- No plan is generated until interpreted rules are displayed.
- Ambiguous instructions are marked “Needs clarification.”
- The original instruction is preserved for editing.
- The app never claims to understand a rule it could not structure.

---

## 8.5 Daily and weekly plan generation

### Launch options

- Today
- Seven days

Meal types:

- Breakfast
- Lunch
- Dinner

Snacks are deferred until after launch because they complicate nutrition allocation without strengthening the primary dinner-planning use case.

### Generation inputs

- Selected household members
- Allergy and avoidance rules
- Nutrition requirements
- Natural-language rules
- Requested meals and dates
- Meals recently shown or rejected
- Available ingredients, when supplied

### Ranking principles

Candidate meals should be ranked using:

1. Safety validity
2. Hard-rule compliance
3. Nutrition compliance
4. Household practicality
5. Ingredient availability and overlap
6. Preparation time
7. Household feedback
8. Variety

### Plan results

Each meal card shows:

- Meal name and image
- Day and meal type
- Estimated cooking time
- Per-member calories and protein
- Key reason tags
- Swap and Lock actions

### Accepting a plan

The user taps **Use this plan**. This action:

- Saves the plan
- Replaces the prior active plan after confirmation
- Builds or updates the shopping list
- Preserves locked meals when regenerating

### Acceptance criteria

- A single failed meal does not fail the whole plan when alternatives exist.
- Generation progress uses honest status messages and can be cancelled.
- Returning to the app after interruption restores the result or resumes safely.
- Duplicate dinners are avoided within the generated week unless explicitly allowed.

---

## 8.6 Shared meal and personalized portions

### Purpose

Minimize household cooking while honoring individual requirements.

### Behavior

The generator should:

1. Select a shared base recipe.
2. Calculate total household quantity.
3. Determine a portion for each member.
4. Create an individual substitution only when required.

Example:

```text
Chicken vegetable rice bowl

Adult 1: 220 g chicken + 180 g rice
Adult 2: 150 g chicken + 110 g rice
Child:    90 g chicken + 80 g rice
```

If a member cannot eat the base ingredient:

```text
For Anaya: replace paneer with tofu and prepare separately.
```

### Acceptance criteria

- Total ingredient quantities reconcile with member portions, allowing reasonable preparation loss.
- A substitution is never shown without allergy revalidation.
- Cooking instructions identify when an allergen-safe portion must be separated.
- The user can switch between household totals and member portions.

---

## 8.7 Swap and Lock

### Swap

Swapping opens a bottom sheet with optional reasons:

- Something different
- Too much work
- Too expensive
- Family will not eat this
- Wrong ingredients
- Other instruction

The replacement must preserve all hard constraints and should respond to the selected reason.

### Lock

A locked meal remains unchanged when the user regenerates the rest of the day or week.

### Acceptance criteria

- Users can undo the most recent swap.
- Swapping one meal does not alter unrelated meals.
- Locked meals remain visually identifiable and accessible.
- If locked meals make the remaining plan impossible, the app explains the conflict.

---

## 8.8 Recommendation explanation and practicality

### User-facing explanation

Each meal should show two or three useful reason tags, such as:

- Safe for all selected members
- Meets 30 g protein minimum
- Uses ingredients already available
- Ready in 25 minutes
- Matches Tuesday's vegetarian rule

Do not display an opaque numeric AI score.

### Internal practicality validation

Before a recommendation appears, verify:

- All declared allergies and exclusions
- Nutrition target compliance
- Time-of-day rules
- Preparation time
- Required equipment when known
- Ingredient quantity consistency
- Excessive repetition
- Recent rejection history
- Number of unique ingredients introduced

### Acceptance criteria

- Reason tags reflect actual calculated properties.
- No tag is generated solely from unverified model text.
- A user can open “Why this meal?” for a concise expanded explanation.

---

## 8.9 Conflict detection

### Purpose

Prevent the system from returning convincing but invalid meals.

### Example

```text
We couldn't satisfy every requirement.

The 50 g protein minimum conflicts with the 300-calorie
maximum and the current ingredient restrictions.

[ Change calorie range ]
[ Change protein target ]
[ Show closest matches ]
```

### Behavior

- Identify the smallest set of conflicting rules when possible.
- Never change an allergy rule as a suggested resolution.
- Offer direct links to edit the relevant settings.
- “Show closest matches” must state exactly which non-safety constraint is missed.

### Acceptance criteria

- Safety constraints are never relaxed.
- The error identifies actionable rules rather than displaying a generic failure.
- User input remains intact after resolving a conflict.

---

## 8.10 Cook with what I have

### Purpose

Suggest relevant meals using ingredients currently available.

### Launch input methods

- Type ingredients
- Speak ingredients using iOS dictation

Fridge-photo recognition is deferred.

### Controls

Missing ingredients:

- Nothing else
- Up to 2 ingredients
- Up to 5 ingredients

Cooking time:

- 15 minutes
- 30 minutes
- Any

Meal type:

- Breakfast
- Lunch
- Dinner

### Results

Organize results into:

1. Can cook now
2. Missing one ingredient
3. Missing two or more ingredients

Each result shows:

- Ingredients used
- Missing ingredients
- Cooking time
- Constraint and nutrition status
- Add missing items to List

### Ingredient rules

- Water, salt, and optional garnish do not count as meaningful missing ingredients.
- The user can mark a detected ingredient as unavailable.
- Household rules apply automatically.
- The same recommendation explanation system applies.

### Acceptance criteria

- Results never include a declared allergen for a selected member.
- The number of missing ingredients is accurate.
- Adding missing ingredients does not duplicate existing list items.
- The user's entered ingredients remain available when returning from a recipe.

---

## 8.11 Recipe and cook mode

### Recipe detail

Show:

- Meal name and image
- Total time
- Household servings
- Per-member portions
- Calories and protein estimates
- Ingredients
- Numbered instructions
- Relevant allergy notice
- Add missing items to List
- Start cooking

### Cook mode

- One instruction step at a time
- Large text and controls
- Previous and Next buttons reachable with one hand
- Screen remains awake while cook mode is active, with user permission
- Ingredient quantities available without leaving the current step
- Timers use native iOS timer interaction where practical

### Acceptance criteria

- Dynamic Type does not truncate essential instructions.
- Cook mode remains usable in landscape and portrait.
- Progress is preserved if the app moves to the background.

---

## 8.12 Shopping list

### Purpose

Turn an accepted plan into an actionable list without becoming a full grocery platform.

### Launch behavior

- Consolidate duplicate ingredients.
- Normalize compatible units where reliable.
- Group into broad categories such as Produce, Protein, Dairy and Alternatives, Pantry, and Other.
- Allow adding, editing, deleting, and checking items.
- Show which meals require an item.
- Offer Undo after deletion or accidental completion.

### Quantity behavior

Example:

```text
Onions — 5
Monday curry: 2
Wednesday pasta: 1
Friday wraps: 2
```

If units cannot be combined reliably, keep separate entries rather than producing a misleading total.

### Acceptance criteria

- Swapping a meal updates only affected shopping items.
- Locked meals retain their ingredients.
- Manually added items are not removed when the plan changes.
- The user can clear checked items with confirmation and undo.

---

## 8.13 Lightweight meal feedback

### Prompt

After a planned meal time or when a user marks a recipe cooked:

```text
How was this meal?
[ Loved it ] [ Okay ] [ Don't suggest again ]
```

Optional reasons:

- Too expensive
- Too difficult
- Too spicy
- Took too long
- Family disliked it
- Portion too small
- Portion too large

### Behavior

- “Don't suggest again” excludes that exact recipe unless reset in settings.
- Negative reasons adjust ranking but do not create unreviewed allergy rules.
- Prompts can be dismissed and notification-based prompts are opt-in.

### Acceptance criteria

- Feedback takes no more than two taps.
- Users can review and remove prior exclusions.
- Feedback improves later ranking without changing safety settings.

---

## 9. Screen requirements

## 9.1 Welcome

Content:

- Clear value proposition
- One primary CTA: “Create my meal plan”
- Secondary CTA: “I already have a plan” only if account sync exists
- Short safety statement concerning allergy information

Avoid feature carousels and account walls before setup.

## 9.2 Setup progress

Use a four-stage progress indicator:

1. Household
2. Food rules
3. Nutrition
4. Instructions

Each screen uses one clear title, supporting text, and a sticky bottom Continue button. Continue remains disabled only when required information is invalid.

## 9.3 Home

Recommended hierarchy:

1. Contextual greeting or next meal
2. Plan today
3. Plan my week
4. Cook with what I have
5. Current plan preview
6. Recent favorites, only if enough data exists

Do not place promotional content above the primary actions.

## 9.4 Plan

- Segmented control: Today / Week
- Horizontal date selection for Today
- Vertical day sections for Week
- Meal cards grouped by breakfast, lunch, and dinner
- Persistent “Use this plan” CTA for an unaccepted generated plan
- Regenerate unlocked meals action placed in an overflow menu to prevent accidents

## 9.5 Cook

- Ingredient token field
- Dictation action
- Recent ingredients
- Missing-item and time filters
- Results grouped by availability

## 9.6 List

- Category sections
- Add item field
- Item checkboxes with large hit targets
- Meal-source disclosure on tap
- Progress indicator such as “12 of 20 items collected”

## 9.7 Household settings

- Members
- Allergies
- Intolerances and avoidances
- Nutrition targets
- Saved instructions
- Excluded meals
- Units and language
- Data export and account, when available

---

## 10. iOS UX requirements

### 10.1 Platform conventions

- Use SwiftUI-native patterns unless a custom interaction provides clear value.
- Respect Safe Area and keyboard avoidance.
- Support light and dark appearance.
- Support Dynamic Type through accessibility sizes.
- Minimum touch target: 44 × 44 points.
- Use standard navigation titles, sheets, alerts, menus, pickers, and tab bars.
- Use haptic feedback sparingly for selection, successful plan acceptance, and errors.
- Support swipe actions as shortcuts only; every action must also be visible elsewhere.

### 10.2 Visual hierarchy

- One primary action per screen.
- Use cards for meals, not for every piece of content.
- Reserve red and warning iconography for allergens, destructive actions, and genuine errors.
- Show nutrition information compactly; do not let numbers overpower meal selection.
- Avoid excessive gradients, glass effects, animation, and decorative AI indicators.

### 10.3 Copy style

- Use short, direct, non-medical language.
- Say “Avoid milk” rather than “Configure dairy exclusion parameters.”
- Clearly label nutrition as estimated.
- Never use “allergy-safe guaranteed.”
- Errors must say what happened and how to resolve it.

### 10.4 Loading states

Plan generation may show progressive messages such as:

1. Checking household rules
2. Finding practical meals
3. Calculating portions
4. Building your plan

Messages must correspond to actual stages where possible. If generation exceeds the expected duration, allow the user to leave and receive the result when ready.

### 10.5 Empty states

Every empty state must offer one next action:

- No active plan → Plan my week
- No ingredients → Add ingredients
- Empty shopping list → Create from current plan
- No feedback history → No explanation needed; omit the section

---

## 11. Accessibility requirements

- Meet WCAG 2.2 AA contrast targets where applicable.
- Support VoiceOver labels, hints, logical reading order, and rotor navigation.
- Never communicate allergy status through color alone.
- Support Dynamic Type without clipping or horizontal scrolling of essential content.
- Provide text alternatives for recipe images.
- Respect Reduce Motion and Reduce Transparency settings.
- Ensure charts or nutrition indicators also expose numeric text.
- Support external keyboard navigation on iPad-compatible layouts, even though iPhone is the initial design target.

---

## 12. Safety and data quality

### 12.1 Allergy safety

- Allergy rules are deterministic filters, not soft model prompts.
- Recipe ingredients and substitutions must pass structured allergen checks.
- Generated text cannot override the structured safety result.
- Packaged and compound ingredients receive a verification notice.
- Cross-contact cannot be guaranteed and must be communicated appropriately.

### 12.2 Nutrition

- Nutrition values must identify their data source internally.
- Values are estimates unless tied to verified product data.
- Portions and recipe totals must be mathematically consistent.
- The app does not prescribe targets or replace professional medical advice.

### 12.3 Generated content

- Recipe steps must be validated for ingredient consistency, cooking temperature, and reasonable timing before publication.
- High-risk cooking guidance must use reviewed templates or trusted sources.
- The product should prefer a curated recipe base over unrestricted recipe invention at launch.

---

## 13. Data model overview

### Household

- Identifier
- Member count
- Default units
- Saved household rules
- Created and updated timestamps

### Member

- Identifier
- Display label
- Adult or child classification
- Allergies
- Intolerances
- Avoidances
- Calorie range per meal
- Protein minimum per meal

### Rule

- Identifier
- Original user text, when applicable
- Structured type
- Target member or household
- Meal type
- Day or recurrence
- Ingredient or category
- Minimum, maximum, or exclusion value
- Priority
- Active status

### Recipe

- Identifier
- Name
- Ingredients and normalized quantities
- Instructions
- Servings
- Preparation and cooking time
- Nutrition per base serving
- Allergen metadata
- Equipment requirements
- Validation status

### Plan

- Identifier
- Date range
- Selected members
- Meal entries
- Locked state by meal
- Applied rules
- Generation status
- Accepted state

### Feedback

- Recipe identifier
- Rating
- Reasons
- Member or household scope
- Timestamp

---

## 14. Analytics and product measurement

Collect only data necessary to improve the product, with clear consent and privacy controls.

### Primary funnel

- Setup started
- Each setup stage completed
- Rules confirmed
- Generation started
- Valid plan generated
- Plan accepted
- Shopping list opened

### Core metrics

- Percentage of new users who generate a first plan
- Median time from app open to first generated plan
- Percentage of generated plans accepted
- Swaps per accepted plan
- Constraint-conflict rate
- Seven-day and thirty-day retention
- Weekly plans generated per active household
- Cook-with-ingredients searches resulting in a recipe opened
- Meals marked Loved, Okay, or Never suggest again

### Quality guardrails

- Allergy-rule violation reports
- Incorrect nutrition reports
- Shopping-list quantity corrections
- Generation failures
- Recipes rejected for impracticality
- Plans abandoned after repeated swaps

The team should prioritize quality guardrails over increasing the raw number of generated plans.

---

## 15. Notifications

Notifications are not required for the initial validation build. If added during launch, they must be opt-in and limited to:

- Upcoming meal requires thawing or advance preparation
- User-selected meal reminder
- Generated plan is ready after background processing

Do not send generic engagement reminders, recipe promotions, or repeated feedback requests.

---

## 16. Monetization considerations

Monetization should occur after the user sees a valid sample plan.

### Suggested free experience

- Household setup
- Limited daily generation
- Limited cook-with-ingredients searches
- Basic recipe and shopping-list access

### Suggested premium experience

- Unlimited weekly plans and swaps
- Multiple saved household configurations
- Advanced nutrition and recurring rules
- Extended history and preference learning
- Future meal-prep and leftover planning

Do not place allergy safety controls, correction of inaccurate results, or data export behind a paywall.

Pricing requires separate market and conversion testing and is outside this PRD.

---

## 17. Release scope

## 17.1 MVP — required

- Four-stage household setup
- Household-wide and individual-member rules
- Allergies, intolerances, and avoidances
- Optional protein and calorie requirements
- Natural-language instructions with confirmation
- Today and seven-day generation
- Breakfast, lunch, and dinner selection
- Shared meals with individualized portions
- Safe member substitutions
- Swap and Lock
- Recommendation explanations
- Conflict detection
- Typed and spoken “Cook with what I have”
- Recipe details and basic cook mode
- Consolidated editable shopping list
- Lightweight meal feedback
- Native iOS accessibility and dark mode

## 17.2 Phase 2 — validate before building

- Planned leftovers
- Combined meal-prep workflow
- Family sharing and real-time list sync
- Simple pantry staples
- Budget styles: Economical, Balanced, Flexible
- Fourteen-day planning
- Kitchen-equipment restrictions
- Fridge-photo ingredient recognition
- More detailed recurrence and schedule rules

Each Phase 2 feature should require evidence from interviews, support requests, usage behavior, or repeated feedback.

## 17.3 Later possibilities

- Receipt or barcode scanning
- Grocery price data
- Calendar integration
- Dietitian-reviewed plan collections
- Regional recipe packs
- Grocery delivery integration
- Nutrition-platform integration
- Preparation and freezer schedules

## 17.4 Explicitly excluded

- Social feed and creator economy
- Followers, public profiles, and recipe likes
- General-purpose calorie diary
- Exercise or weight tracking
- Meal-photo calorie estimation
- Restaurant logging
- Automatic grocery ordering at launch
- Complex inventory accounting
- Chatbot-only interaction

---

## 18. Risks and mitigations

### Risk: AI misunderstands a user instruction

**Mitigation:** Convert instructions into structured rules and require confirmation before generation.

### Risk: A generated meal violates an allergy

**Mitigation:** Use deterministic structured filtering before and after generation. Never rely only on model text.

### Risk: Nutrition estimates are inaccurate

**Mitigation:** Use a consistent nutrition data source, expose estimates clearly, and validate portion calculations.

### Risk: Generated recipes are unrealistic

**Mitigation:** Begin with a curated and validated recipe collection. Use generation primarily for selection, adaptation, and portioning.

### Risk: Onboarding feels too long

**Mitigation:** Maintain four visible stages, make nutrition optional, provide common chips, and allow member-specific details only when selected.

### Risk: Too many features obscure the primary actions

**Mitigation:** Preserve the three Home actions and require evidence before promoting Phase 2 functionality.

### Risk: Shopping quantities become unreliable after swaps

**Mitigation:** Recalculate affected ingredient deltas transactionally and preserve manual list items separately.

---

## 19. Launch acceptance criteria

The MVP is ready for external testing when:

1. A new user can generate a plan without creating an account.
2. The median first-plan journey can be completed in less than two minutes during usability testing.
3. Allergy rules are enforced through structured validation.
4. A user can create household-wide and member-specific rules.
5. Natural-language rules are displayed for confirmation before generation.
6. Generated meals show per-member portions and nutrition estimates.
7. A user can swap one meal and preserve locked meals.
8. Conflicting requirements produce a specific, actionable explanation.
9. Cook with what I have accurately distinguishes available and missing ingredients.
10. An accepted plan produces a consolidated, editable shopping list.
11. Core screens support VoiceOver, Dynamic Type, dark mode, and 44-point touch targets.
12. No launch-blocking flow requires access to a deferred feature.

---

## 20. Open product decisions

These questions require product testing or business decisions before final implementation:

- Initial geographic market and recipe cuisine coverage
- Whether breakfast and lunch are enabled by default or requested explicitly
- Nutrition database provider
- Curated recipe sourcing and licensing model
- Authentication and synchronization provider
- Free-generation limits and premium pricing
- Minimum supported iOS version
- Whether child profiles require additional safety language
- Supported languages and measurement systems at launch
- Whether plans are generated locally, on a server, or through a hybrid approach

---

## 21. Recommended design validation

Before full engineering implementation, test a clickable prototype with at least five household meal planners who have different dietary constraints.

Each participant should attempt to:

1. Create a four-person household.
2. Assign a milk allergy to one member.
3. Set a 30 g protein minimum for another member.
4. Add “paneer at lunch but not dinner.”
5. Generate a weekly plan.
6. Replace one meal and lock another.
7. Find a recipe using four ingredients at home.
8. Open and modify the shopping list.

Measure completion time, errors, hesitation, misunderstood labels, and whether participants trust the generated result. Any recurring confusion in the four-stage setup should be resolved before adding Phase 2 features.
