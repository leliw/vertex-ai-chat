#!/bin/sh
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload &
cd ../frontend
ng serve -o
cd ..
killall uvicorn