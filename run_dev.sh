#!/bin/sh

cd frontend
ng serve -o &
cd ..
cd backend
.venv/bin/python -m uvicorn app.main:app --reload
cd ..
#pkill -f ".venv/bin/python -m uvicorn main:app --reload"
pkill -f "ng serve -o"

