FROM ghcr.io/asreview/asreview:v1.2.1

RUN apt-get update && \
    apt-get install -y curl ca-certificates amqp-tools python3 \
       --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    && pip install boto3 pika

#### Don't modify above this line

# For sbert:
# RUN pip install --user sentence-transformers~=2.2.2

# For doc2vec:
# RUN pip install --user gensim~=4.2.0

#### Don't modify below this line

COPY ./worker-receiver.py /app/worker-receiver.py
COPY ./worker.sh /app/worker.sh

ENV PYTHONUNBUFFERED=1
WORKDIR /app/workdir

ENTRYPOINT [ "/bin/bash", "/app/worker.sh" ]
