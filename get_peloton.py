import pylotoncycle
import requests
import sqlite3
import os
from datetime import datetime
import calendar


def get_db_connection():
    db_conn = sqlite3.connect("/app/workout_data.db")
    db_conn.row_factory = sqlite3.Row
    return db_conn


pelo_username_secret = os.environ["pelo_username_secret"]
pelo_password_secret = os.environ["pelo_password_secret"]

pelo_conn = pylotoncycle.PylotonCycle(pelo_username_secret, pelo_password_secret)
workouts = pelo_conn.GetRecentWorkouts()

with get_db_connection() as conn:

    for w in workouts:

        workout_id = w["id"]

        # See if workout_id is anywhere in the database
        cur = conn.cursor()
        cur.execute(
            "SELECT workout_id FROM workouts WHERE workout_id=?",
            (workout_id,),
        )
        result = cur.fetchone()

        if not result:

            resp = pelo_conn.GetWorkoutMetricsById(workout_id)

            date = datetime.fromtimestamp(w["created_at"]).strftime("%Y-%m-%d %H:%M:%S")

            if not w["title"]:
                w["title"] = w["ride"]["title"]

            cur.execute(
                "INSERT INTO workouts (workout_id, date, created_at, total_time, pr, title, total_output, distance, calories) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                [
                    workout_id,
                    date,
                    w["created_at"],
                    round((w["end_time"] - w["created_at"]) / 60, 2),
                    w["is_total_work_personal_record"],
                    w["title"],
                    resp["summaries"][0]["value"],
                    resp["summaries"][1]["value"],
                    resp["summaries"][2]["value"],
                ],
            )
            conn.commit()
