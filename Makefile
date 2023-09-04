
load_local:
	export ENV=LOCAL && locust -f tests/load/locustfile.py --logfile locust.log

load_dev:
	export ENV=DEV && locust -f tests/load/locustfile.py --logfile locust.log

run_local:
	uvicorn  app:app --host 0.0.0.0 --port 8000 --timeout-keep-alive 5 --log-level debug --reload

