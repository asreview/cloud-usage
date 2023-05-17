FROM ghcr.io/asreview/asreview:v1.2

RUN apt-get update && \
    apt-get install -y curl ca-certificates amqp-tools python \
       --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    && pip install pika

COPY ./split-file.py /app/split-file.py
COPY ./tasker-send.py /app/tasker-send.py
COPY ./tasker.sh /app/tasker.sh

ENV PYTHONUNBUFFERED=1
WORKDIR /app/workdir

#### Don't modify above this line
COPY data /app/data

#### Don't modify below this line
ENTRYPOINT [ "/bin/bash", "/app/tasker.sh" ]
