import pylotoncycle
import sqlite3
import os
from datetime import datetime


def get_db_connection():
    db_conn = sqlite3.connect("/app/workout_data.db")
    db_conn.row_factory = sqlite3.Row
    return db_conn


class Workout(object):
    def __init__(
        self,
        workout_id,
        date,
        created_at,
        total_time,
        pr,
        title,
        output,
        distance,
        calories,
    ):
        self.workout_id = workout_id
        self.date = date
        self.created_at = created_at
        self.total_time = total_time
        self.pr = pr
        self.title = title
        self.output = output
        self.distance = distance
        self.calories = calories

    def __repr__(self):
        return str(vars(self))


pelo_username_secret = os.environ["pelo_username_secret"]
pelo_password_secret = os.environ["pelo_password_secret"]

pelo_conn = pylotoncycle.PylotonCycle(pelo_username_secret, pelo_password_secret)
workouts = pelo_conn.GetRecentWorkouts()

with get_db_connection() as conn:

    for w in workouts:

        if w["fitness_discipline"] == "cycling":

            workout = Workout(
                w["id"],
                datetime.fromtimestamp(w["created_at"]).strftime("%Y-%m-%d %H:%M:%S"),
                w["created_at"],
                round((w["end_time"] - w["created_at"]) / 60, 2),
                w["is_total_work_personal_record"],
                w["title"],
                None,
                None,
                None,
            )

            # See if workout_id is anywhere in the database
            cur = conn.cursor()
            cur.execute(
                "SELECT workout_id FROM workouts WHERE workout_id=?",
                (workout.workout_id,),
            )
            result = cur.fetchone()

            if not result:

                resp = pelo_conn.GetWorkoutMetricsById(workout.workout_id)

                if not w["title"]:
                    workout.title = w["ride"]["title"]

                # Check if the workout is in metric or imperial or doesn't exist in the dataset

                try:

                    if w["ride"]["distance_unit"] == "metric":

                        workout.output = resp["summaries"][1]["value"]
                        workout.distance = resp["summaries"][2]["value"]
                        workout.calories = resp["summaries"][3]["value"]

                    if not w["ride"]["distance_unit"]:

                        workout.output = resp["summaries"][0]["value"]
                        workout.distance = resp["summaries"][1]["value"]
                        workout.calories = resp["summaries"][2]["value"]

                except KeyError:

                    workout.output = resp["summaries"][0]["value"]
                    workout.distance = resp["summaries"][1]["value"]
                    workout.calories = resp["summaries"][2]["value"]

                cur.execute(
                    "INSERT INTO workouts (workout_id, "
                    "date, "
                    "created_at, "
                    "total_time, "
                    "pr, title, "
                    "output, "
                    "distance, "
                    "calories) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    [
                        workout.workout_id,
                        workout.date,
                        workout.created_at,
                        workout.total_time,
                        workout.pr,
                        workout.title,
                        workout.output,
                        workout.distance,
                        workout.calories,
                    ],
                )
                conn.commit()
