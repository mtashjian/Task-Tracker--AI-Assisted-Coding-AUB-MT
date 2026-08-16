# Feature 1 prompt log


## 1. Incremental implementation plan
**Weak Prompt**
Add due dates and an overdue filter to my task tracker.
**What I asked**  
Before writing code, produce an incremental plan for Feature 1 (Due Date + Overdue Filter). Output: Step | Exact file/section | Change | Verification before next step. Sequence: backend, backend tests, frontend, manual browser check, Break Test. No Feature 2. No new libraries or database.

**What AI returned**  
A step table: backend model/storage/API (1.1–1.5), backend tests (2.1–2.4), frontend modal/card (3.1–3.3), manual checklist (4), Break Test (5). Locked decisions: `due_date` is a date; past dates rejected; today allowed; overdue = past + not null + not `Done`; frontend does not send `overdue`.


## 2. Backend

**What I asked**  
One focused backend change: optional `due_date` + overdue filter. State which functions/classes to change and why, then a focused diff for `app/models.py`, `app/storage.py`, `app/main.py` only. Later: “apply”.

**What AI returned**  
Change list: `TaskCreate` / `TaskUpdate` / `TaskResponse` (`due_date` + past-date validator); `add_task` persist; `get_all_tasks` + `list_tasks` `overdue` query. Leave `update_task` as `exclude_unset`. Diffs for those three files. After “apply”: wrote the diffs; existing tests 20/20 green.


## 3. Test scenarios

**What I asked**  
Do not write test code. Brainstorm 6 focused backend scenarios. Assignment coverage: valid due date, invalid format, overdue detection, updating due date, overdue filter only overdue. Also one preservation case if it matches the model. Output: Priority | Test scenario | Setup | Expected result | Requirement protected.

**What AI returned**  
Six P1 rows: valid create (today); invalid format; PATCH due date; overdue detection (seed past dates in storage); `overdue=true` only overdue; unrelated PATCH does not drop `due_date` (DD-2 AC5).

## 4. One pytest

### 4.1 Valid due date on create

**What I asked**  
Write one pytest for “Valid due date on create.” Output only the new test function. Then: “ADD THE FUNCTION TO THE FILE.”

**What AI returned**  
`test_create_task_due_date_today_returns_201_and_echoes_date` — POST today, 201, echo `due_date`. Note to add `from datetime import date`. After “ADD THE FUNCTION”: appended that test + import; test passed.

**What I accepted**  
That function, added to `tests/test_tasks.py`.


### 4.2 Due date not specified on create

**What I asked**  
Write one pytest for “DUE DATE NOT SPECIFIED ON CREATE.” Output only the new test function.

**What AI returned**  
Added `test_create_task_without_due_date_returns_201_and_due_date_null` — POST title only, 201, `due_date is None`. Test passed.


### 4.3 Overdue detection

**What I asked**  
Write one pytest for “Overdue detection.” Output only the new test function.

**What AI returned**  
Added `test_get_tasks_overdue_detects_past_due_non_done_only`. Setup via API; past dates written into `storage._tasks`. `overdue=true` = ToDo+yesterday only; `overdue=false` = Done+past, null, today. No `overdue` field on the body. Test passed.

### 4.4 Overdue filter returns only overdue tasks

**What I asked**  
Write one pytest for “Overdue filter returns only overdue tasks.” Output only the new test function.

**What AI returned**  
Added `test_get_tasks_overdue_true_returns_only_overdue_tasks`. Two overdue (ToDo + InProgress) plus today/null neighbors; `GET ?overdue=true` is 200 and only those two IDs. Test passed.
# Feature 2 prompt log

## 1. Evaluation of implementation choices (Feature 1 and Feature 2)

**What I asked**  
Two lightweight approaches each for Feature 1 (Due Date + Overdue Filter) and Feature 2 (Search + Combined Filters), using the repo and final decisions in `user-stories.md`. Compare due date / overdue / `GET /tasks?overdue=` / frontend for Feature 1; storage vs another abstraction, AND with existing filters, and frontend filter state for Feature 2. Score simplicity, testability, compatibility, size of change, risk. Keep current architecture; no DB/ORM/new frontend/new deps/filter framework/saved views/tags. Do not choose. Output: Feature | Option | Implementation outline | Advantages | Weaknesses | Files affected.

**What AI returned**  
A 4-row table. Feature 1A: Pydantic `date`, overdue in `get_all_tasks`, API `overdue` query, local card paint. Feature 1B: shared UTC `today()` + `is_overdue()`, route-level overdue filter, UTC card paint. Feature 2A: add `search` on `get_all_tasks`; JS `searchQuery`. Feature 2B: `matches_search()` helper; search box as only frontend state. Both Feature 1 options keep API `?overdue=` (DD-4) and frontend not sending it (DD-5).
**What I accepted**  
Option A

## 2. Frontend

**What I asked**  
Add Feature 2 to existing `frontend/index.html`. Preserve columns, priority sort, loading/empty/ready/error, drag-and-drop, create/edit modal, and Feature 1 due-date / overdue card behavior. Follow approved SR-1–SR-4. Compact bar above the board: text search, status, priority, overdue only if in the approved design, combinations, and a clear/reset. Use `GET /tasks` query params. Do not hide empty columns, do not client-filter, no new framework/library, no full-file rewrite. Output: functions/sections to change, focused diff, browser checklist.

**What AI returned**  
A compact `#filter-bar` above the board: search, status (`ToDo` / `InProgress` / `Done`), priority (`High` / `Medium` / `Low`), Clear. No overdue control (approved Feature 1/2 frontend does not send `overdue`). New `buildTasksUrl()` reads the controls; omits blank/whitespace `search` and empty “All” selects; `fetchTasks()` uses that URL. Wired search input (300ms debounce), select `change`, Enter, and Clear. Left render/modal/dnd unchanged. Browser checklist for individual and combined filters.


