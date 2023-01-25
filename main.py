import time
from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
import sqlite3

app = FastAPI()

app.mount("/app/static", StaticFiles(directory="/app/static"), name="static")
templates = Jinja2Templates(directory="/app/templates")


def get_db_connection():
    conn = sqlite3.connect("/app/workout_data.db")
    conn.execute("pragma journal_mode=wal")
    conn.row_factory = sqlite3.Row
    return conn


@app.exception_handler(StarletteHTTPException)
async def my_custom_exception_handler(Request: Request, exc: StarletteHTTPException):
    context = {"request": Request}
    return templates.TemplateResponse("ouch.html", context)


@app.get("/robots.txt")
def robots():
    data = """\
    User-agent: * 
    Disallow: \
    """
    return Response(content=data, media_type="text/plain")


@app.get("/", response_class=HTMLResponse)
async def index(Request: Request):
    now = time.time()
    conn = get_db_connection()

    last_workout = conn.execute(
        "SELECT * FROM workouts ORDER BY created_at DESC LIMIT 1"
    ).fetchall()

    total_distance = conn.execute("SELECT SUM(distance) FROM workouts").fetchone()

    total_calories = conn.execute("SELECT SUM(calories) FROM workouts").fetchone()

    total_output = conn.execute("SELECT SUM(output) FROM workouts").fetchone()

    total_rides = conn.execute("SELECT COUNT(*) FROM workouts").fetchone()

    total_time = conn.execute("SELECT SUM(total_time) FROM workouts").fetchone()

    workouts_last_week = conn.execute(
        f"SELECT COUNT(*) FROM workouts WHERE created_at > ({now} - 604800) ORDER BY created_at DESC",
    ).fetchone()

    prs_last_week = conn.execute(
        f"SELECT * FROM workouts WHERE created_at > ({now} - 604800) AND pr = 1 ORDER BY created_at DESC",
    ).fetchall()

    total_distance_last_week = conn.execute(
        f"SELECT SUM(distance) FROM workouts WHERE created_at > ({now} - 604800) ORDER BY created_at DESC"
    ).fetchone()

    total_calories_last_week = conn.execute(
        f"SELECT SUM(calories) FROM workouts WHERE created_at > ({now} - 604800) ORDER BY created_at DESC"
    ).fetchone()

    output_last_week = conn.execute(
        f"SELECT SUM(output) FROM workouts WHERE created_at > ({now} - 604800) ORDER BY created_at DESC"
    ).fetchone()

    total_rides_last_week = conn.execute(
        f"SELECT COUNT(*) FROM workouts WHERE created_at > ({now} - 604800) ORDER BY created_at DESC"
    ).fetchone()

    total_time_last_week = conn.execute(
        f"SELECT SUM(total_time) FROM workouts WHERE created_at > ({now} - 604800) ORDER BY created_at DESC"
    ).fetchone()

    conn.close()
    context = {
        "request": Request,
        "total_distance": total_distance,
        "total_calories": total_calories,
        "total_output": total_output,
        "total_rides": total_rides,
        "total_time": total_time,
        "total_distance_last_week": total_distance_last_week,
        "total_calories_last_week": total_calories_last_week,
        "output_last_week": output_last_week,
        "total_rides_last_week": total_rides_last_week,
        "total_time_last_week": total_time_last_week,
        "workouts_last_week": workouts_last_week,
        "prs_last_week": prs_last_week,
        "last_workout": last_workout,
        "now": now,
    }
    return templates.TemplateResponse("index.html", context)
