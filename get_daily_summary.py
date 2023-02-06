import requests
import sqlite3
import os
import time

now = time.time()


def get_db_connection():
    conn = sqlite3.connect("/app/workout_data.db")
    conn.row_factory = sqlite3.Row
    return conn


OPENAI_SECRET = os.environ["OPENAI_SECRET"]

with get_db_connection() as conn:
    cur = conn.cursor()

    last_workout = conn.execute(
        "SELECT * FROM workouts ORDER BY created_at DESC LIMIT 1"
    ).fetchall()

    total_distance = conn.execute("SELECT SUM(distance) FROM workouts").fetchone()

    total_calories = conn.execute("SELECT SUM(calories) FROM workouts").fetchone()

    total_output = conn.execute("SELECT SUM(output) FROM workouts").fetchone()

    total_rides = conn.execute("SELECT COUNT(*) FROM workouts").fetchone()

    total_time = conn.execute("SELECT SUM(total_time) FROM workouts").fetchone()

    prs_last_week = conn.execute(
        f"SELECT * FROM workouts WHERE created_at > ({now} - 604800) AND pr = 1 ORDER BY created_at DESC",
    ).fetchall()

    total_distance_last_week = conn.execute(
        f"SELECT SUM(distance) FROM workouts WHERE created_at > ({now} - 604800) ORDER BY created_at DESC"
    ).fetchone()

    total_calories_last_week = conn.execute(
        f"SELECT SUM(calories) FROM workouts WHERE created_at > ({now} - 604800) ORDER BY created_at DESC"
    ).fetchone()

    total_output_last_week = conn.execute(
        f"SELECT SUM(output) FROM workouts WHERE created_at > ({now} - 604800) ORDER BY created_at DESC"
    ).fetchone()

    total_rides_last_week = conn.execute(
        f"SELECT COUNT(*) FROM workouts WHERE created_at > ({now} - 604800) ORDER BY created_at DESC"
    ).fetchone()

    total_time_last_week = conn.execute(
        f"SELECT SUM(total_time) FROM workouts WHERE created_at > ({now} - 604800) ORDER BY created_at DESC"
    ).fetchone()

    # OpenAI enrichment

    url = "https://api.openai.com/v1/completions"
    headers = {
        "Authorization": "Bearer " + OPENAI_SECRET,
        "Content-Type": "application/json",
    }
    json = {
        "model": "text-davinci-003",
        "prompt": f"""Imagine you are a person tracking their fitness stats.
        
        Here are your stats in the past week:
        {total_distance_last_week[0]} miles biked last week
        {total_calories_last_week[0]} calories burned last week
        {total_time_last_week[0]} minutes biked last week
        {total_rides_last_week[0]} rides last week
        {len(prs_last_week)} PRs last week
        
        If I take the calories burned in the past week and divide by 3500, that should be how many pounds I've lost through cycling
        in the past week.
        
        If I take the calories burned in the past week and divide by 508, that should be how many Shrimp Tempura rolls I've burned this week. 
        
        Write a 4-6 sentence summary of your fitness stats for the week and some of the food stats mentioned above.""",
        "max_tokens": 1000,
        "temperature": 0,
    }
    ai_request = requests.post(url, headers=headers, json=json).json()
    ai_summary = ai_request["choices"][0]["text"].lstrip()

    # Add the info to the database

    cur.execute("UPDATE daily_summary SET summary = ?", (ai_summary,))

    conn.commit()
