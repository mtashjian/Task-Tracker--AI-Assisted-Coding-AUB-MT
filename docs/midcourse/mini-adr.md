# ADR-002: Use Inline Filtering (Option A) for Due Date/Overdue and Search Features

**Status:** Accepted
**Date:** August 15, 2026
**Decision Owners:** Project Team
**Related:** ADR-001 (JSON File Storage)

## Context

Two new features are being added to the existing Task Tracker Kanban board and API:

1. **Due Date + Overdue Filter** — tasks gain an optional `due_date`, and `GET /tasks` gains an `overdue` filter (kept on the API per DD-4; the board itself never sends it, per DD-5).
2. **Search + Combined Filters** — `GET /tasks` gains a `search` filter that matches against title, description, and assignee, combinable with `status`, `priority`, and `overdue`.

The current implementation is a single in-memory `storage.get_all_tasks(status, priority)` function that applies sequential AND filters, backed by Pydantic `TaskCreate` / `TaskUpdate` / `TaskResponse` models, with status transition rules in `business_rules.py` and a single vanilla `frontend/index.html`. There is no database, no extra dependencies, and `date` is already imported (unused) in both `models.py` and `storage.py`.

For each feature, two implementation options were evaluated:

- **Option A** extends the existing pattern directly: a new optional field/argument and one more `if` inside `get_all_tasks`, matching how `status` and `priority` already work.
- **Option B** introduces a small amount of new structure: a shared `today()` / `is_overdue()` helper (Feature 1) or a `matches_search()` helper (Feature 2), with filtering logic partially or fully moved out of `get_all_tasks` and into the route layer.

## Decision

**Option A will be used for both Feature 1 and Feature 2.**

### Feature 1 — Due Date + Overdue Filter (Option A)

- `due_date: Optional[date] = None` added to `TaskCreate`, `TaskUpdate`, and `TaskResponse`.
- Past `due_date` values are allowed on create/update so overdue work can be entered; today itself is allowed and is not overdue. Invalid date format is a 422 from Pydantic.
- PATCH with `due_date: null` clears the field via the existing `exclude_unset` pattern.
- "Overdue" is computed inline inside `get_all_tasks` as: `due_date is not None and due_date < date.today() and status != Done`.
- `GET /tasks` gains `overdue: bool | None = None`, applied alongside `status`/`priority` with the same sequential-AND pattern. Omitted means no overdue filtering.
- Frontend adds a `<input type="date">` on the task form, sends `due_date` or `null`, displays the date on the card, and paints `.card.overdue` plus an **Overdue** warning when the card's `due_date` is earlier than the browser's local `YYYY-MM-DD` and status is not `Done`. The board never sends `overdue` as a query param.

### Feature 2 — Search + Combined Filters (Option A)

- `get_all_tasks` gains `search: str | None = None`. If `search` is missing or blank after `strip()`, the filter is skipped; otherwise a task is kept when `search.casefold()` is a substring of `title`, `description`, or `assignee` (null `assignee` is skipped unless title/description already match).
- Search combines with `status`, `priority`, and `overdue` using the same sequential AND already in use; invalid `status`/`priority` still 422 before storage runs.
- Frontend adds a header search `<input>`. On input/Enter, `fetchTasks()` reads the box directly (trimmed) and includes `search` in the query only when non-empty. No dedicated `searchQuery` JS variable is introduced — the input element is the single source of truth, which is the smallest version of Option A's frontend.

## Rationale

### Consistency with the existing pattern

Both features extend `get_all_tasks` the same way `status` and `priority` already work: an optional keyword argument plus one additional `if`. A future contributor reading `storage.py` sees one filtering idiom, not two.

### Smallest surface area

- Feature 1, Option A: one field, one validator, one `if`.
- Feature 2, Option A: one argument, one `if`.
- No new modules, no new helper functions, no route-level list logic that duplicates what storage already does.

### Testability is still straightforward

All new behavior is reachable and verifiable over HTTP:
- Past-date rejection → 422 on create/update.
- Overdue filtering → one more `params=` case in `GET /tasks` tests.
- Search → one more `params=` case, plus combination cases with `status`/`priority`/`overdue`.

### No new dependencies or architecture

Both options satisfy the shared constraint of no new dependencies, no ORM/DB, no new frontend framework, no filter DSL, no saved views, no tags, and no query types beyond `status`, `priority`, `overdue`, and `search` — but Option A reaches that outcome with fewer moving parts than Option B.

## Consequences

### Positive consequences

* Filtering logic for all four query parameters (`status`, `priority`, `overdue`, `search`) lives in one place: `get_all_tasks`.
* Existing list tests are unaffected, since new parameters default to `None`/unfiltered.
* Smaller diffs across `app/models.py`, `app/storage.py`, `app/main.py`, and `frontend/index.html` than Option B would require.
* The frontend for Feature 2 has no dedicated `searchQuery` state to keep in sync — the search box itself is the state, so there is nothing to desync.

### Negative consequences (accepted trade-offs)

* **Server/local date disagreement (Feature 1):** overdue is computed with `date.today()`, which is server-local, while `created_at` elsewhere is UTC. Near midnight, or if server and browser are in different time zones, the API's `overdue=true` filter and the frontend's local-date red-card paint can disagree on which tasks are overdue.
* **Duplicated overdue logic (Feature 1):** the overdue rule (`due_date < today`, not null, not `Done`) exists inline in `storage.py` and is re-implemented in JS for card painting. A future change to the rule (e.g., grace period, different `Done`-equivalent statuses) requires updating both places.
* **`get_all_tasks` grows another concern (Feature 2):** the function now mixes field-equality filters (`status`, `priority`), a date/status-derived filter (`overdue`), and a text-search filter in one place. This is accepted as still readable at current scale, but is the first sign the function may need to be split later.
* **Blank vs. omitted search:** `search=""` and no `search` param must be normalized identically (both = "no filter"). This is a one-line `strip()` check, but it's a spot where a regression could silently break "clear search."
* **No standalone unit-testable helpers:** because search and overdue live inline rather than as `matches_search()` / `is_overdue()` functions, they can only be exercised through `get_all_tasks` or HTTP, not in isolation. Given the small size of the logic, this is judged acceptable for now.

These trade-offs were deliberately accepted in exchange for keeping both features as small, single-pattern extensions of the existing storage function, consistent with this project's learning-focused scope (see ADR-001).

## Alternatives Considered

**Option B** (shared `today()`/`is_overdue()` helper for Feature 1; `matches_search()` helper for Feature 2, with route-level filtering) was considered for both features.

Option B would have:
- Made "today" a single, mockable source of truth, simplifying tests for past-date validation and overdue filtering.
- Kept `get_all_tasks`'s signature limited to `status`/`priority`, moving `overdue` filtering to the route.
- Made search a small, independently unit-testable pure function.

It was not selected because, at the current project size, it introduces more files/functions and a second filtering style (route-level vs. storage-level) for a benefit — better testability and reduced duplication — that isn't yet justified by the complexity of the filtering rules involved.

## Reconsideration Triggers

This decision should be revisited if any of the following occur:

* The server and expected users are regularly in different time zones and the local/UTC "today" mismatch causes real confusion or bug reports.
* The overdue rule changes in a way that's error-prone to keep in sync between `storage.py` and the frontend (e.g., new terminal statuses, grace periods).
* `get_all_tasks` grows further (e.g., sorting, pagination, additional filters) to the point where mixing filter styles inline becomes hard to read or test.
* Search matching rules become more complex (e.g., multi-field weighting, fuzzy matching) such that a pure, independently testable `matches_search()` becomes worth the extra module.
* Automated tests for "today"-dependent behavior (past-date validation, overdue) become flaky or hard to set up without a mockable time source.

Until one of these applies, Option A remains the selected approach for both features.
