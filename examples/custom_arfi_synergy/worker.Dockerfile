FROM ghcr.io/asreview/asreview:v1.2

RUN apt-get update && \
    apt-get install -y curl ca-certificates amqp-tools python \
       --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    && pip install pika

#### Don't modify above this line

# For sbert:
# RUN pip install sentence-transformers~=2.2.2

# For doc2vec:
RUN pip install gensim~=4.2.0

# RUN pip install --upgrade asreview-makita~=0.6.3
# RUN pip install https://github.com/jteijema/asreview-reusable-fe/archive/main.zip
# RUN pip install https://github.com/jteijema/asreview-XGBoost/archive/main.zip

# For neural netowrk
# RUN pip install tensorflow~=2.9.1

#### Don't modify below this line

COPY ./worker-receiver.py /app/worker-receiver.py
COPY ./worker.sh /app/worker.sh

ENV PYTHONUNBUFFERED=1
WORKDIR /app/workdir

ENTRYPOINT [ "/bin/bash", "/app/worker.sh" ]
