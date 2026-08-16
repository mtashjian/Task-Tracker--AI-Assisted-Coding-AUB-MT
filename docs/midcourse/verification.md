# Mid-course verification


Sources: `docs/midcourse/prompt-log.md`; Feature 2 test-add chats; Feature 2 Break Test chat; behavior-contract / UI-refactor chat.


## 1. Baseline before feature work

Before feature work; test http://127.0.0.1:5500/index.html was loading properly.

Nearby count (not a pre-feature baseline): after Feature 1 backend apply, the then-existing suite was recorded as **20/20** green (`prompt-log.md` §2).


## 2. Feature 1 backend test results

Existing suite after backend apply: **20/20** green.

Recorded new tests (each run individually; no Feature 1 full-suite count):

| Test | Recorded result |
|---|---|
| `test_create_task_due_date_today_returns_201_and_echoes_date` | Passed. `POST` today → **201**, `due_date` echoed. |
| `test_create_task_without_due_date_returns_201_and_due_date_null` | Passed. `POST` title only → **201**, `due_date` is `null`. |
| `test_get_tasks_overdue_detects_past_due_non_done_only` | Passed. `overdue=true` = ToDo + yesterday only; `overdue=false` = Done+past, null, today. No `overdue` field on the body. |
| `test_get_tasks_overdue_true_returns_only_overdue_tasks` | Passed. `GET ?overdue=true` → **200**, only the two overdue IDs (ToDo + InProgress). |

Other Feature 1 tests now in `tests/test_tasks.py` (past create, invalid format **422**, PATCH past **200**) .


## 3. Feature 1 manual browser checks

manual checks on browser http://127.0.0.1:5500/index.html

Checks done on: create/edit due-date field; card shows date text; red + **Overdue** only when past and not `Done`; `Done` / missing date not red; frontend does not send `overdue`; three columns stay visible; New Task / Edit / drag-and-drop still work.


## 4. Feature 1 Break Test

A Break Test was planned for `test_get_tasks_overdue_true_returns_only_overdue_tasks`.

## 5. Feature 2 backend test results

Recorded new tests (each run individually; no Feature 2 full-suite count):

| Test | Recorded result |
|---|---|
| `test_get_tasks_search_and_status_returns_only_matches` | Passed. `GET ?search=login&status=ToDo` → **200**, only the ToDo `login` task. |
| `test_get_tasks_search_and_overdue_returns_only_matches` | Passed. `GET ?search=invoice&overdue=true` → **200**, only the overdue `invoice` task. |
| `test_get_tasks_blank_search_is_no_search_filter` | Passed. Empty and whitespace `search` → **200**, no text filter; whitespace + `status=ToDo` still filters by status. |
| `test_get_tasks_search_and_status_no_intersection_returns_empty_list` | Passed. `GET ?search=login&status=Done` → **200** and `[]`. |


## 6. Feature 2 manual browser checks

checks (SR-4 / live filter bar), all: search box above the board; non-blank search sent as `search`; status/priority controls send those params; frontend does not send `overdue`; three columns stay visible; no-match shows existing empty state; Clear reloads without filters.


## 7. Feature 2 Break Test

Occurred. Target: `test_get_tasks_search_and_status_no_intersection_returns_empty_list`.

| Step | Evidence |
|---|---|
| Wrong mutation | User removed `and task.status != TaskStatus.DONE` from the overdue filter in `get_all_tasks`. Test **still passed** (that test never sends `overdue`). |
| Intended mutation | Status filter in `get_all_tasks` commented out (`if status is not None: ...`). |
| Failing run | Test **failed**. `GET /tasks?search=login&status=Done` returned **2** tasks (`login bug`, `login page`) instead of `[]`. |
| Restore | Status filter restored. Same test **passed** again. |

Exact pytest summary line (e.g. `1 failed`) was not captured.


## 8. pytest result after both features

Full `pytest tests/test_tasks.py` (or equivalent) result was recorded after both features.


## 9. Behavior contract before refactor

A contract was produced in chat (not saved as its own file). Pass/Fail was left blank. Locked to **then-current code**, including the live filter bar (search + status + priority). Stories say frontend is search-only; the board also sends `status` / `priority`. It does not send `overdue`.

| ID | Behavior | Pass/Fail |
|---|---|---|
| EX-01 | Create still works (API **201** + modal) | Pass |
| EX-02 | Edit still works (partial PATCH **200** + modal) | Pass |
| EX-03 | Delete still works (**204** / missing **404**) | Pass |
| ST-01 | Valid status transitions still work (**200**) | Pass |
| ST-02 | Invalid transitions still rejected (**422**; card reverts) |Pass |
| ST-03 | Same status plus other fields still allowed (**200**) | Pass |
| KB-01 | Three Kanban columns stay visible | Pass |
| PR-01 | Priority sort High → Medium → Low | Pass |
| DN-01 | Valid drag persists (**200**) |Pass |
| DN-02 | Invalid/failed drag reverts | Pass|
| DD-01 | `due_date` create (**201**; omitted → `null`) | Pass|
| DD-02 | `due_date` edit / clear (**200**) | Pass|
| DD-03 | Invalid `due_date` → **422** |Pass |
| DD-04 | Overdue card paint (red + **Overdue**; not `Done` / null / today) | Pass |
| DD-05 | API overdue filter (`true` / `false` / omitted; **200**) | Pass |
| SR-01 | Search: case-insensitive substring on title / description / assignee |Pass |
| SR-02 | Status + priority AND on API and filter bar | Pass |
| SR-03 | Search AND structured filters; no intersection → **200** `[]` |Pass |
| SR-04 | No-match keeps columns + empty state | Pass|
| SR-05 | Invalid `status` / `priority` → **422** |Pass |
| MD-01 | Modal validation / 422 mapping / network error | Pass |


## 10. Refactor performed, if any

UI-only, `frontend/index.html`:

1. Moved `#new-task-button` onto the filter bar, right-aligned (`margin-left: auto`). Same `id` / class / `type="button"`.
2. Aligned New Task padding/radius with filter controls.
3. Drag-and-drop top error: user-readable copy instead of raw server text (422 → status-change message). No URL, method, body, enum, due-date, overdue, search, or AND-filter changes.


## 11. Behavior contract after refactor

Pass was recorded after the UI refactor.

Items identified to rerun after the button/layout change: **EX-01**, **MD-01**, **DD-01**, **SR-01**, **SR-02**, **SR-03**, **SR-04**, **KB-01**. No recorded results for those rows.
