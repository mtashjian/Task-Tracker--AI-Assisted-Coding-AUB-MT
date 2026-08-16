# Mid-course user stories

Role for every story: **team member**.

## 1. Due Date + Overdue Filter

### AI assumption corrected

| | |
|---|---|
| **Original AI assumption** | `due_date` as datetime; overdue meaning left unspecified (including whether `Done` tasks can be overdue); frontend might send an `overdue` query filter. |
| **Final decision** | `due_date` is a **date**, not datetime. Overdue means `due_date < today` on the **API’s calendar date**, `due_date` is not `null`, and status is not `Done`. Frontend does **not** send `overdue`; cards show the date text, turn red, and show an **Overdue** warning when overdue. Past dates are **allowed** on create and update so overdue work can be entered; **today is allowed** and is not overdue. |

### DD-1

**User story:** As a team member, I want to optionally set a due date when I create a task so I know when it should be finished.

**Acceptance criteria:**

1. `POST /tasks` without `due_date` returns 201 and `due_date` is `null`.
2. `POST /tasks` with `due_date` equal to today returns 201 and echoes that date.
3. `POST /tasks` with `due_date` after today returns 201.
4. `POST /tasks` with `due_date` before today returns 201 and stores that date (task is overdue if status is not `Done`).
5. `POST /tasks` with an invalid date format (e.g. `not-a-date`, `2026-13-40`) returns 422.
6. Existing create rules still hold: blank title 422, unknown fields 422, defaults `status=ToDo`, `priority=Medium`, `description=""`, `assignee=null`.

**Notes / AI assumptions:** Not specified by the assignment (human-corrected): `due_date` is a **date**, not datetime. Past dates are **allowed** on create so overdue cards can be entered; **today is allowed** and is not overdue. Assignment asked for optional due date on create and tests for valid date + invalid format.

### DD-2

**User story:** As a team member, I want to change or clear a task’s due date when I update it so the date stays accurate.

**Acceptance criteria:**

1. `PATCH /tasks/{id}` with `due_date` equal to today, in the future, or before today returns 200 and stores that value.
2. `PATCH` with a past `due_date` stores the date whether or not `status` is also sent; the task is overdue if status is not `Done`.
3. `PATCH` with invalid date format returns 422.
4. `PATCH` with `due_date: null` clears `due_date`.
5. `PATCH` that omits `due_date` leaves `due_date` unchanged.
6. Missing task still returns 404.
7. Existing status-transition rules are unchanged.

**Notes / AI assumptions:** Past dates are **allowed** on PATCH so overdue work can be recorded or corrected. **Today is allowed** and is not overdue. Assignment asked for update support and tests for updating due date.

### DD-4

**User story:** As a team member, I want to list overdue vs not-overdue tasks so I can focus on work that is past due.

**Acceptance criteria:**

1. Overdue means `due_date < today`, `due_date` is not `null`, and `status` is not `Done`. `due_date` and `today` use the **same calendar date the API uses**.
2. `GET /tasks?overdue=true` returns only overdue tasks, HTTP 200.
3. `GET /tasks?overdue=false` returns **not overdue only** (includes `Done` even if `due_date < today`, tasks with `due_date` null, and `due_date >= today`).
4. Omitted `overdue` applies no overdue filter.
5. No matches return 200 and `[]`.
6. `overdue` combines with `status` and `priority` using **AND**.
7. Invalid typed existing filters (e.g. `status=Nope`) still return 422.

**Notes / AI assumptions:** Not specified by the assignment (human-corrected): exact overdue definition; **completed (`Done`) tasks are not overdue**; null due date is not overdue; query-only `overdue=true` / `overdue=false` (no overdue field on the task body); omitted `overdue` means no filter; **`today` is the API’s calendar date**. Assignment asked for overdue detection/filtering and tests for overdue detection + filtering overdue tasks. Frontend does **not** send this param (see DD-5).

### DD-5

**User story:** As a team member, I want to enter a due date in the task modal and see the date on the card, with overdue work highlighted in red, so I can spot late tasks on the board.

**Acceptance criteria:**

1. Create and edit modal include a due-date field.
2. Saving create/edit sends `due_date` on `POST`/`PATCH` (or `null` if empty).
3. Card shows due-date **text** when `due_date` is present.
4. Card is **red** and shows an **Overdue** warning only when `due_date < today` **and** status is not `Done`.
5. `Done` cards are not red and have no Overdue warning even if `due_date < today`.
6. Missing `due_date` is not red and has no Overdue warning.
7. Frontend does **not** send `overdue`; it only paints cards.
8. All three Kanban columns stay visible; empty columns keep the existing empty state.
9. Existing New Task, Edit, and drag-and-drop still work.

**Notes / AI assumptions:** Assignment allowed “overdue filter or visual indicator.” Human-corrected: visual indicator only (red card + Overdue warning), **not** a frontend overdue filter control; also show the date text; red **excludes `Done`**. Modal due date is in assignment scope. Past dates may be entered on create/edit.

## 2. Search + Combined Filters

### AI assumption corrected

| | |
|---|---|
| **Original AI assumption** | Search title and description only (as the assignment stated); case sensitivity and blank search left unspecified. |
| **Final decision** | Search is a case-insensitive **substring** on **any** of `title`, `description`, or `assignee`. Query param name is `search`. Empty or whitespace search means **no search filter**. Frontend search lives in the header and sends `search` only. |

### SR-1

**User story:** As a team member, I want to search tasks by text so I can find a task by wording in its title, description, or assignee.

**Acceptance criteria:**

1. `GET /tasks?search=<text>` matches a case-insensitive **substring** if it appears in **any** of `title`, `description`, or `assignee`.
2. A match in only one of those fields is enough.
3. `null` assignee does not match unless title or description matches.
4. No matches return HTTP 200 and `[]`.
5. Omitting `search` does not filter by text (existing list behavior).

**Notes / AI assumptions:** Assignment specified search of title and description only. Human-corrected: also search **assignee**. Not specified by the assignment (human-corrected): **case-insensitive**; **substring** match; query param name is `search`.

### SR-2

**User story:** As a team member, I want a blank search to mean “no search” so clearing the box shows the full board again.

**Acceptance criteria:**

1. Empty `search` (`""`) is treated as no search filter.
2. Whitespace-only `search` (e.g. `"   "`) is treated as no search filter.
3. In both cases the response is HTTP 200 and uses only any other provided filters (`status`, `priority`, `overdue`).
4. Frontend: empty/whitespace box **omits** the `search` query param.

**Notes / AI assumptions:** Not specified by the assignment (human-corrected): blank/whitespace search means **no search parameter**, not “match nothing” and not 422.

### SR-3

**User story:** As a team member, I want search to combine with status, priority, and overdue filters so I can narrow the list without extra requests.

**Acceptance criteria:**

1. When more than one of `search`, `status`, `priority`, `overdue` is present, results must satisfy **all** of them (AND).
2. Combined filters with no matches return 200 and `[]`.
3. Invalid typed `status` or `priority` still return 422, including when `search` is also sent.
4. Valid `search` plus valid `status`/`priority` returns 200 and only matching tasks.
5. Existing `GET /tasks` with only `status` and/or `priority` is unchanged.

**Notes / AI assumptions:** Assignment asked to combine search with **status and priority**. Human-approved: same AND also applies to `overdue` when that query param is present. Do not add new filter types beyond these.

### SR-4

**User story:** As a team member, I want a compact search box in the header above the board so I can filter the Kanban view without leaving it.

**Acceptance criteria:**

1. A search control is in the header / compact area above the board.
2. Non-empty, non-whitespace input is sent as `GET /tasks?search=...`.
3. Frontend does **not** send `overdue` (or new status/priority filter controls).
4. After search, all three columns remain visible.
5. If no tasks match, each column shows the existing empty state (not a blank page / error).
6. Board still groups by existing status values `ToDo` / `InProgress` / `Done`.
7. Clearing search reloads without `search` and shows all tasks again.

**Notes / AI assumptions:** Assignment asked for a compact search/filter area. Human-corrected: **search only** in the header; frontend sends `search` and does not add overdue/status/priority UI filters. Keep Kanban empty states as already implemented.
