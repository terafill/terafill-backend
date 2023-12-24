FROM python:3.9.18-slim

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git && \
    apt-get install -y make && \    
    apt-get install -y gcc default-libmysqlclient-dev pkg-config && \
    rm -rf /var/lib/apt/lists/*


COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

RUN mkdir /terafill_backend

COPY ./app /terafill_backend/app
COPY main.py /terafill_backend/main.py
COPY Makefile /terafill_backend/Makefile
COPY .env.local /terafill_backend/.env.local

WORKDIR /terafill_backend

CMD ["make", "run_local"]
