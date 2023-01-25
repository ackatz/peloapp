import main
from fastapi.testclient import TestClient
import pytest
import sqlite3


client = TestClient(main.app)


@pytest.fixture
def setup_database():
    """Fixture to set up the in-memory database with test data"""
    conn = sqlite3.connect("/app/workout_data.db")
    cursor = conn.cursor()
    cursor.execute(
        """
	    CREATE TABLE workouts
        (workout_id, date, created_at, total_time, pr, title, output, distance, calories)
        """
    )
    workout_sample_data = [
        (
            "0843353daa63879a84c3dae4d07b23b5",
            "2021-01-01 00:00:00",
            "1234567890",
            "1.00",
            "1",
            "Sample Article Name",
            "1.00",
            "1.00",
            "1.00",
        )
    ]
    cursor.executemany(
        "INSERT INTO workouts VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", workout_sample_data
    )
    conn.commit()
    yield conn


def test_read_index(setup_database):
    response = client.get("/")
    assert response.status_code == 200
    assert "<title>My Peloton Stats</title>" in response.text


def test_read_robots_txt():
    response = client.get("/robots.txt")
    assert response.status_code == 200


def test_read_404_page():
    response = client.get("/404")
    assert response.status_code == 200
