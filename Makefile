PORT ?= 8000
MYSQL_DUMP_VERSION ?= vx
DATABASE ?= terafill
ORG_ID ?= terafill
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
	docker build -t terafill-backend .	

run_local_docker:
	docker run -e MYSQL_HOST=terafill_mysql -e MYSQL_PORT=3306 -e PORT=8001 -e WORKERS=2 --cpuset-cpus="0-1" --memory=2g --rm --name terafill_backend1 --network terafill-network -h 127.0.0.1 -d terafill-backend
	docker run -e MYSQL_HOST=terafill_mysql -e MYSQL_PORT=3306 -e PORT=8002 -e WORKERS=2 --cpuset-cpus="2-3" --memory=2g --rm --name terafill_backend2 --network terafill-network -h 127.0.0.1 -d terafill-backend
	docker run -e MYSQL_HOST=terafill_mysql -e MYSQL_PORT=3306 -e PORT=8003 -e WORKERS=2 --cpuset-cpus="4-5" --memory=2g --rm --name terafill_backend3 --network terafill-network -h 127.0.0.1 -d terafill-backend
	docker run -e "SERVICE_NAME=terafill-backend-service" \
	-e "SERVICE_TAGS=fastapi,api" \
	-e "SERVICE_8001_CHECK_HTTP=/api/v1/hello" \
	-e "SERVICE_8001_CHECK_INTERVAL=10s" \
	-e MYSQL_HOST=terafill_mysql -e MYSQL_PORT=3306 -e PORT=8004 -e WORKERS=2 --cpuset-cpus="6-7" --memory=2g --rm --name terafill_backend4 --network terafill-network -h 127.0.0.1 -d terafill-backend

run_otel_local:
	# docker run --rm --name terafill_prometheus --network terafill-network -p 9090:9090 --volume $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml -d terafill-prometheus
	docker run --rm --cpuset-cpus="10-10" --memory=2g --name grafana --network terafill-network -p 3000:3000 -d grafana/grafana-oss:latest
	docker run --network terafill-network --cpuset-cpus="10-10" --memory=4g --rm --name jaeger   -e COLLECTOR_ZIPKIN_HOST_PORT=:9411   -p 6831:6831/udp   -p 6832:6832/udp   -p 5778:5778   -p 16686:16686   -p 4317:4317   -p 4318:4318   -p 14250:14250   -p 14268:14268   -p 14269:14269   -p 9411:9411 -d  jaegertracing/all-in-one:1.51
	# docker run --network terafill-network --cpuset-cpus="10-10" --memory=2g --rm --name zipkin -d -p 9411:9411 openzipkin/zipkin

backup_mysql_local:
	sudo mysqldump  terafill > ./mysql_dumps/mysql_dump_${MYSQL_DUMP_VERSION}.sql

backup_mysql:
	pscale database dump ${DATABASE} ${ENV@L} --output mysql_dumps/${ENV@L}/$(date +"%Y-%m-%d_%H-%M-%S") --service-token ${PLANET_SCALE_SERVICE_TOKEN} --service-token-id ${PLANET_SCALE_SERVICE_TOKEN} --org ${ORG_ID} --debug

build_mysql_local:
	docker build -f db.Dockerfile -t terafill-mysql .

run_mysql_local:
	docker run --network terafill-network --cpuset-cpus="8-8" --memory=4g --rm -p 3306:3306 --name terafill_mysql -d terafill-mysql

run_mysql_cli_local:
	docker run --rm -it --network terafill-network mysql mysql -h 0.0.0.0 -u root -p

cleanup:	
	docker stop terafill_mysql terafill_backend1 terafill_backend2 terafill_backend3 terafill_backend4 terafill_nginx jaeger grafana

build_nginx_docker:
	docker build -f nginx/nginx.Dockerfile -t terafill-nginx .

run_nginx_docker:
	docker run -p 0.0.0.0:8000:8000 --rm --cpuset-cpus="9-9" --memory=2g --name terafill_nginx --network terafill-network -d terafill-nginx

ping_nginx_docker:
	docker run --network terafill-network -it --rm curlimages/curl http://terafill_nginx:8000/api/v1/hello

run_local_docker_cluster: run_otel_local run_mysql_local run_local_docker run_nginx_docker
	echo "Create a local terafill backend cluster"
