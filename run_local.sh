# set -a
# source .env
# set +a
uvicorn  app:app --host 0.0.0.0 --port 8000 --timeout-keep-alive 5 --log-level debug --reload
