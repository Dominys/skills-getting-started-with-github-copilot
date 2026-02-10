from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def remove_participant_if_present(activity_name: str, email: str) -> None:
    client.delete(f"/activities/{activity_name}/participants", params={"email": email})


def test_get_activities_returns_activity_data():
    response = client.get("/activities")

    assert response.status_code == 200
    activities = response.json()
    assert "Chess Club" in activities
    assert "participants" in activities["Chess Club"]


def test_signup_adds_participant():
    activity_name = "Chess Club"
    email = "test_signup@mergington.edu"

    remove_participant_if_present(activity_name, email)

    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 200
    activities = client.get("/activities").json()
    assert email in activities[activity_name]["participants"]


def test_delete_removes_participant():
    activity_name = "Chess Club"
    email = "test_remove@mergington.edu"

    remove_participant_if_present(activity_name, email)
    client.post(f"/activities/{activity_name}/signup", params={"email": email})

    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})

    assert response.status_code == 200
    activities = client.get("/activities").json()
    assert email not in activities[activity_name]["participants"]


def test_signup_duplicate_returns_400():
    activity_name = "Chess Club"
    email = "test_duplicate@mergington.edu"

    remove_participant_if_present(activity_name, email)
    client.post(f"/activities/{activity_name}/signup", params={"email": email})

    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_signup_invalid_activity_returns_404():
    response = client.post("/activities/Unknown%20Club/signup", params={"email": "test@mergington.edu"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_delete_missing_participant_returns_404():
    activity_name = "Chess Club"
    email = "missing@mergington.edu"

    remove_participant_if_present(activity_name, email)

    response = client.delete(
        f"/activities/{activity_name}/participants", params={"email": email}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student not signed up"
