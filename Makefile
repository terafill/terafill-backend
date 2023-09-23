PORT ?= 8000
MYSQL_DUMP_VERSION ?= vx
DATABASE ?= keylance
ORG_ID ?= keylance
WORKERS ?= 1

setup_tests:
	ulimit -n 4096

load_local: setup_tests
	export ENV=LOCAL && locust -f tests/load/locustfile.py --logfile locust.log

load_dev:
	export ENV=DEV && locust -f tests/load/locustfile.py --logfile locust.log

run_local: setup_tests
	# hypercorn app:app --bind 0.0.0.0:$(PORT) -w ${WORKERS} -k trio
	gunicorn -k uvicorn.workers.UvicornWorker -w ${WORKERS} -b 0.0.0.0:$(PORT) app:app --log-level debug --access-logfile access.log --error-logfile error.log
	# uvicorn  app:app --host 0.0.0.0 --port $(PORT) --workers ${WORKERS}

build_docker:
	docker build -t keylance-backend .	

run_local_docker:
	docker run --cpus=2 --memory=2g --rm --name keylance_backend --network host -p 0.0.0.0:8000:8000 -v $(shell pwd):/app keylance-backend

run_otel_local:
	docker run --cpus=1 --memory=2g --rm --name jaeger   -e COLLECTOR_ZIPKIN_HOST_PORT=:9411   -p 6831:6831/udp   -p 6832:6832/udp   -p 5778:5778   -p 16686:16686   -p 4317:4317   -p 4318:4318   -p 14250:14250   -p 14268:14268   -p 14269:14269   -p 9411:9411   jaegertracing/all-in-one:1.48

backup_mysql_local:
	sudo mysqldump  keylance > ./mysql_dumps/mysql_dump_${MYSQL_DUMP_VERSION}.sql

backend_mysql:
	pscale database dump ${DATABASE} ${ENV@L} --output mysql_dumps/${ENV@L}/$(date +"%Y-%m-%d_%H-%M-%S") --service-token ${PLANET_SCALE_SERVICE_TOKEN} --service-token-id ${PLANET_SCALE_SERVICE_TOKEN} --org ${ORG_ID} --debug