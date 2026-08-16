from datetime import date, timedelta


def test_create_task_valid_returns_201_with_full_body(client):
    payload = {
        "title": "Buy milk",
        "description": "2%",
        "status": "ToDo",
        "priority": "High",
        "assignee": "alice",
    }
    r = client.post("/tasks", json=payload)
    assert r.status_code == 201
    body = r.json()
    assert body["title"] == "Buy milk"
    assert body["description"] == "2%"
    assert body["status"] == "ToDo"
    assert body["priority"] == "High"
    assert body["assignee"] == "alice"
    assert "id" in body
    assert "created_at" in body
    assert "updated_at" in body


def test_create_task_missing_title_returns_422(client):
    r = client.post("/tasks", json={"description": "no title"})
    assert r.status_code == 422


def test_create_task_blank_title_returns_422(client):
    r = client.post("/tasks", json={"title": "   "})
    assert r.status_code == 422


def test_create_task_invalid_priority_returns_422(client):
    r = client.post("/tasks", json={"title": "x", "priority": "Urgent"})
    assert r.status_code == 422


def test_create_task_unknown_field_returns_422(client):
    r = client.post("/tasks", json={"title": "x", "foo": "bar"})
    assert r.status_code == 422


def test_list_tasks_empty_returns_200_and_empty_list(client):
    r = client.get("/tasks")
    assert r.status_code == 200
    assert r.json() == []


def test_list_tasks_filter_by_status_no_match_returns_200_and_empty_list(client, created_task):
    r = client.get("/tasks", params={"status": "Done"})
    assert r.status_code == 200
    assert r.json() == []


def test_list_tasks_filter_by_priority_returns_only_matches(client):
    client.post("/tasks", json={"title": "low", "priority": "Low"})
    client.post("/tasks", json={"title": "high", "priority": "High"})
    r = client.get("/tasks", params={"priority": "High"})
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 1
    assert body[0]["title"] == "high"
    assert body[0]["priority"] == "High"


def test_get_task_by_id_returns_task(client, created_task):
    task_id = created_task["id"]
    r = client.get(f"/tasks/{task_id}")
    assert r.status_code == 200
    assert r.json()["id"] == task_id
    assert r.json()["title"] == "fixture task"


def test_get_task_by_id_not_found_returns_404_with_detail(client):
    r = client.get("/tasks/does-not-exist")
    assert r.status_code == 404
    assert r.json()["detail"] == "Task with id does-not-exist not found"


def test_patch_partial_update_keeps_other_fields(client, created_task):
    task_id = created_task["id"]
    r = client.patch(f"/tasks/{task_id}", json={"title": "updated title"})
    assert r.status_code == 200
    body = r.json()
    assert body["title"] == "updated title"
    assert body["description"] == created_task["description"]
    assert body["status"] == created_task["status"]
    assert body["priority"] == created_task["priority"]
    assert body["assignee"] == created_task["assignee"]
    assert body["id"] == task_id


def test_patch_not_found_returns_404(client):
    r = client.patch("/tasks/does-not-exist", json={"title": "x"})
    assert r.status_code == 404
    assert r.json()["detail"] == "Task with id does-not-exist not found"


def test_patch_valid_transition_todo_to_inprogress_returns_200(client, created_task):
    task_id = created_task["id"]
    assert created_task["status"] == "ToDo"
    r = client.patch(f"/tasks/{task_id}", json={"status": "InProgress"})
    assert r.status_code == 200
    assert r.json()["status"] == "InProgress"


def test_patch_invalid_transition_todo_to_done_returns_422(client, created_task):
    task_id = created_task["id"]
    assert created_task["status"] == "ToDo"
    r = client.patch(f"/tasks/{task_id}", json={"status": "Done"})
    assert r.status_code == 422


def test_patch_same_status_returns_422(client, created_task):
    task_id = created_task["id"]
    assert created_task["status"] == "ToDo"
    r = client.patch(f"/tasks/{task_id}", json={"status": "ToDo"})
    assert r.status_code == 422


def test_patch_priority_only_update_succeeds_without_status_error(client, created_task):
    task_id = created_task["id"]
    r = client.patch(f"/tasks/{task_id}", json={"priority": "High"})
    assert r.status_code == 200
    body = r.json()
    assert body["priority"] == "High"
    assert body["status"] == created_task["status"]


def test_patch_same_status_with_other_fields_succeeds(client, created_task):
    task_id = created_task["id"]
    assert created_task["status"] == "ToDo"
    r = client.patch(
        f"/tasks/{task_id}",
        json={
            "status": "ToDo",
            "title": "renamed",
            "description": "updated",
            "priority": "High",
            "assignee": "bob",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ToDo"
    assert body["title"] == "renamed"
    assert body["description"] == "updated"
    assert body["priority"] == "High"
    assert body["assignee"] == "bob"


def test_delete_existing_returns_204_no_body(client, created_task):
    task_id = created_task["id"]
    r = client.delete(f"/tasks/{task_id}")
    assert r.status_code == 204
    assert r.content == b""


def test_delete_missing_returns_404(client):
    r = client.delete("/tasks/does-not-exist")
    assert r.status_code == 404
    assert r.json()["detail"] == "Task with id does-not-exist not found"


def test_patch_empty_json_object_body_returns_422_and_error_detail(client):
    # Arrange: create a task to update
    create_r = client.post("/tasks", json={"title": "Task for empty patch"})
    assert create_r.status_code == 201
    task = create_r.json()
    task_id = task["id"]

    # Act: send an empty JSON object as the PATCH body
    r = client.patch(f"/tasks/{task_id}", json={})

    # Assert: empty update is treated as no-op and returns the existing task
    assert r.status_code == 200
    body = r.json()
    assert body == task


def test_create_task_due_date_today_returns_201_and_echoes_date(client):
    today = date.today().isoformat()
    r = client.post("/tasks", json={"title": "Due today", "due_date": today})
    assert r.status_code == 201
    body = r.json()
    assert body["due_date"] == today


def test_create_task_due_date_past_returns_201_and_echoes_date(client):
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    r = client.post("/tasks", json={"title": "Overdue", "due_date": yesterday})
    assert r.status_code == 201
    assert r.json()["due_date"] == yesterday


def test_create_task_without_due_date_returns_201_and_due_date_null(client):
    r = client.post("/tasks", json={"title": "No due date"})
    assert r.status_code == 201
    body = r.json()
    assert body["due_date"] is None


def test_create_task_invalid_due_date_format_returns_422(client):
    r = client.post("/tasks", json={"title": "Bad date", "due_date": "not-a-date"})
    assert r.status_code == 422


def test_patch_due_date_past_returns_200_and_stores_date(client, created_task):
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    r = client.patch(f"/tasks/{created_task['id']}", json={"due_date": yesterday})
    assert r.status_code == 200
    assert r.json()["due_date"] == yesterday


def test_get_tasks_overdue_detects_past_due_non_done_only(client):
    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()

    overdue = client.post(
        "/tasks", json={"title": "overdue todo", "due_date": yesterday}
    ).json()
    done_past = client.post(
        "/tasks", json={"title": "done past", "due_date": yesterday}
    ).json()
    no_date = client.post("/tasks", json={"title": "no date"}).json()
    due_today = client.post(
        "/tasks", json={"title": "due today", "due_date": today}
    ).json()

    client.patch(f"/tasks/{done_past['id']}", json={"status": "InProgress"})
    client.patch(f"/tasks/{done_past['id']}", json={"status": "Done"})

    r_true = client.get("/tasks", params={"overdue": True})
    assert r_true.status_code == 200
    true_body = r_true.json()
    assert [task["id"] for task in true_body] == [overdue["id"]]
    assert "overdue" not in true_body[0]

    r_false = client.get("/tasks", params={"overdue": False})
    assert r_false.status_code == 200
    assert {task["id"] for task in r_false.json()} == {
        done_past["id"],
        no_date["id"],
        due_today["id"],
    }


def test_get_tasks_overdue_true_returns_only_overdue_tasks(client):
    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()

    overdue_todo = client.post(
        "/tasks", json={"title": "overdue todo", "due_date": yesterday}
    ).json()
    overdue_wip = client.post(
        "/tasks", json={"title": "overdue wip", "due_date": yesterday}
    ).json()
    client.post("/tasks", json={"title": "due today", "due_date": today})
    client.post("/tasks", json={"title": "no date"})

    client.patch(f"/tasks/{overdue_wip['id']}", json={"status": "InProgress"})

    r = client.get("/tasks", params={"overdue": True})
    assert r.status_code == 200
    assert {task["id"] for task in r.json()} == {
        overdue_todo["id"],
        overdue_wip["id"],
    }


def test_get_tasks_search_and_status_returns_only_matches(client):
    login_todo = client.post(
        "/tasks", json={"title": "login bug"}
    ).json()
    login_wip = client.post(
        "/tasks", json={"title": "login page"}
    ).json()
    client.post("/tasks", json={"title": "signup"})

    client.patch(f"/tasks/{login_wip['id']}", json={"status": "InProgress"})

    r = client.get("/tasks", params={"search": "login", "status": "ToDo"})
    assert r.status_code == 200
    assert [task["id"] for task in r.json()] == [login_todo["id"]]


def test_get_tasks_search_and_overdue_returns_only_matches(client):
    yesterday = (date.today() - timedelta(days=1)).isoformat()

    invoice_overdue = client.post(
        "/tasks", json={"title": "invoice late", "due_date": yesterday}
    ).json()
    client.post("/tasks", json={"title": "invoice later"})
    client.post("/tasks", json={"title": "other", "due_date": yesterday})

    r = client.get("/tasks", params={"search": "invoice", "overdue": True})
    assert r.status_code == 200
    assert [task["id"] for task in r.json()] == [invoice_overdue["id"]]


def test_get_tasks_blank_search_is_no_search_filter(client):
    first = client.post("/tasks", json={"title": "alpha"}).json()
    second = client.post("/tasks", json={"title": "beta"}).json()
    client.patch(f"/tasks/{second['id']}", json={"status": "InProgress"})

    r_empty = client.get("/tasks", params={"search": ""})
    assert r_empty.status_code == 200
    assert {task["id"] for task in r_empty.json()} == {first["id"], second["id"]}

    r_whitespace = client.get("/tasks", params={"search": "   "})
    assert r_whitespace.status_code == 200
    assert {task["id"] for task in r_whitespace.json()} == {first["id"], second["id"]}

    r_with_status = client.get("/tasks", params={"search": "   ", "status": "ToDo"})
    assert r_with_status.status_code == 200
    assert [task["id"] for task in r_with_status.json()] == [first["id"]]


def test_get_tasks_search_and_status_no_intersection_returns_empty_list(client):
    client.post("/tasks", json={"title": "login bug"})
    login_wip = client.post("/tasks", json={"title": "login page"}).json()
    client.patch(f"/tasks/{login_wip['id']}", json={"status": "InProgress"})

    r = client.get("/tasks", params={"search": "login", "status": "Done"})
    assert r.status_code == 200
    assert r.json() == []

