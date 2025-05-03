# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Start Uvicorn server
uvicorn main:app --host 0.0.0.0 --port 7860 --reload
