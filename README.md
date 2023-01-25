# Peloton App

## General Idea

I want to create an app that takes my Peloton stats like distance, calories, etc. and shows them against interesting metrics like:

- Percentage traveled between London and Paris
- Percentage traveled between Los Angeles and New York
- Percentage traveled between Tucson and Phoenix
- Percentage traveled between Denver and Irvine
- Pounds burned based on calories
- Hours/days spent riding
- etc.

Stack:

- FastAPI
- Docker
- Fly.io
- Cron jobs to bring in the newest data
- SQLite to store it
- SQLalchemy to do ORM stuff.

Electric toothbrush: 20 kJ
Small portable speaker: 50 kJ
Handheld gaming device: 60 kJ
Electric razor: 70 kJ
Portable electric heater: 100 kJ
Electric kettle: 120 kJ
Electric stove burner: 150 kJ
Electric blanket: 200 kJ
Portable air conditioner: 250 kJ
Electric lawn mower: 280 kJ
Electric car charger: 290 kJ
Electric bike charger: 300 kJ
Electric bike: 50 kJ
Electric scooter: 100 kJ
Electric wheelchair: 150 kJ
Electric skateboard: 200 kJ
Electric vehicle: 250 kJ
Electric train: 270 kJ
Electric airplane: 280 kJ
Electric boat: 290 kJ

This is the conversion for "you could power X based on your last ride"
