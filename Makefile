
load_local:
	export ENV=LOCAL && locust -f tests/load/locustfile.py --logfile locust.log

load_dev:
	export ENV=DEV && locust -f tests/load/locustfile.py --logfile locust.log

run_local:
	# hypercorn app:app --bind 0.0.0.0:8000 -w 4 -k trio
	gunicorn -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8000 app:app
	# uvicorn  app:app --host 0.0.0.0 --port 8000 --workers 4

build_docker:
	docker build -t keylance-backend .	

run_local_docker:
	docker run --cpus=2 --memory=2g --rm --name keylance_backend --network host -p 0.0.0.0:8000:8000 -v $(shell pwd):/app keylance-backend

run_otel_local:
	docker run --cpus=1 --memory=2g --rm --name jaeger   -e COLLECTOR_ZIPKIN_HOST_PORT=:9411   -p 6831:6831/udp   -p 6832:6832/udp   -p 5778:5778   -p 16686:16686   -p 4317:4317   -p 4318:4318   -p 14250:14250   -p 14268:14268   -p 14269:14269   -p 9411:9411   jaegertracing/all-in-one:1.48
