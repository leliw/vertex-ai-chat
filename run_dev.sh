#!/bin/sh
cd backend
source .venv/bin/activate
uvicorn main:app --reload &
cd ../frontend
ng serve -o
cd ..