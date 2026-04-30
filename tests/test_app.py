from copy import deepcopy

from fastapi.testclient import TestClient
from src.app import app, activities as activity_data

client = TestClient(app)
initial_activities = deepcopy(activity_data)


def reset_activities():
    activity_data.clear()
    activity_data.update(deepcopy(initial_activities))


def setup_function():
    reset_activities()


def teardown_function():
    reset_activities()


def test_root_redirects_to_static_index():
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_list():
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json() == initial_activities


def test_signup_for_activity_adds_participant():
    email = "test@student.edu"
    response = client.post("/activities/Chess Club/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for Chess Club"
    assert email in activity_data["Chess Club"]["participants"]


def test_signup_duplicate_returns_400():
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_signup_missing_activity_returns_404():
    response = client.post(
        "/activities/Nonexistent/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_removes_student():
    email = "emma@mergington.edu"
    response = client.delete(
        "/activities/Programming Class/participants",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from Programming Class"
    assert email not in activity_data["Programming Class"]["participants"]


def test_unregister_missing_participant_returns_404():
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": "unknown@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_unregister_missing_activity_returns_404():
    response = client.delete(
        "/activities/Nonexistent/participants",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
