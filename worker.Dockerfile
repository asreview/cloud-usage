FROM ghcr.io/asreview/asreview:v1.2

RUN apt-get update && \
    apt-get install -y curl ca-certificates amqp-tools python \
       --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    && pip install pika

COPY ./worker-receiver.py /app/worker-receiver.py
COPY ./worker.sh /app/worker.sh

ENV PYTHONUNBUFFERED=1
WORKDIR /app/workdir
#### Don't modify above this line

#### Don't modify below this line
ENTRYPOINT [ "/bin/bash", "/app/worker.sh" ]
