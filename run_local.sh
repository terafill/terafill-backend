set -a
source .env
set +a
uvicorn  app:app --host 0.0.0.0 --port 8000 --workers 1 --reload

