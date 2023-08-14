FROM ghcr.io/asreview/asreview:v1.2.1

RUN apt-get update && \
    apt-get install -y curl ca-certificates amqp-tools python3 \
       --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    && pip install pika

#### Don't modify above this line
# Alternative 1: Copy your data folder
COPY data /app/data
# Alternative 2: Install and synergy-dataset
# RUN pip install synergy-dataset
# RUN mkdir -p /app/data
# RUN synergy get -l -o ./app/data

#### Don't modify below this line

COPY ./custom_arfi.txt.template /app/custom_arfi.txt.template
COPY ./makita-args.txt /app/makita-args.txt
COPY ./split-file.py /app/split-file.py
COPY ./tasker-send.py /app/tasker-send.py
COPY ./tasker.sh /app/tasker.sh

ENV PYTHONUNBUFFERED=1
WORKDIR /app/workdir

ENTRYPOINT [ "/bin/bash", "/app/tasker.sh" ]
