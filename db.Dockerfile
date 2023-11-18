FROM mysql:8.2.0
ENV MYSQL_ROOT_PASSWORD Terafill_backend_123
ENV MYSQL_DATABASE terafill
ENV MYSQL_USER terafill_backend
ENV MYSQL_PASSWORD Terafill_backend_123
COPY ./sql /docker-entrypoint-initdb.d/
