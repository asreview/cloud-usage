#!/usr/bin/env python
import os
import shutil
import subprocess
import sys

import boto3
import pika

RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.environ.get("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.environ.get("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.environ.get("RABBITMQ_PASS", "guest")

S3_REGION_NAME = os.environ.get("S3_REGION_NAME", "")
S3_ENDPOINT_URL = os.environ.get("S3_ENDPOINT_URL", "")
S3_AWS_ACCESS_KEY_ID = os.environ.get("S3_AWS_ACCESS_KEY_ID", "")
S3_AWS_SECRET_ACCESS_KEY = os.environ.get("S3_AWS_SECRET_ACCESS_KEY", "")


class Worker:
    def __init__(self):
        print(f"Logging as {RABBITMQ_USER}")

        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
        parameters = pika.ConnectionParameters(
            RABBITMQ_HOST,
            RABBITMQ_PORT,
            "/",
            credentials,
            heartbeat=3600,
        )

        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        channel.queue_declare(queue="asreview_queue", durable=True)
        channel.queue_declare(queue="tasker")

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue="asreview_queue", on_message_callback=self.callback)

        if S3_ENDPOINT_URL != "":
            self.s3 = boto3.resource(
                "s3",
                region_name=S3_REGION_NAME,
                endpoint_url=S3_ENDPOINT_URL,
                aws_access_key_id=S3_AWS_ACCESS_KEY_ID,
                aws_secret_access_key=S3_AWS_SECRET_ACCESS_KEY,
            )
            self.s3_bucket = self.s3.Bucket("asreview-storage")
        else:
            self.s3 = None
            self.s3_bucket = None
            print("Warning: S3 is not configured. Check the `s3-secret.yml` file.")

        print("[*] Waiting for messages. CTRL+C to exit")
        channel.start_consuming()

    def callback(self, ch, method, properties, body):
        message = body.decode()
        s3_prefix, cmd = message.split("+++")
        print("=> Received %r" % cmd)
        try:
            if "simulate" in cmd:
                split_cmd = cmd.split()
                idx = split_cmd.index("-s")
                filename = f"{split_cmd[idx + 1]}.tmp"
                if os.path.exists(filename):
                    print("Delete tmp file")
                    shutil.rmtree(filename)

            subprocess.run(
                cmd,
                check=True,
                shell=True,
            )

            print("✓ Done")
        except Exception as err:
            if not os.path.exists("issues"):
                os.mkdir("issues")
            with open(f"issues/{RABBITMQ_USER}.txt", "a", encoding="utf-8") as f:
                f.write(cmd)
                f.write(f" msg: {str(err)}")
                f.write("--------")
            print("x Error. Storing issue on folder issues/")

        ch.basic_publish("", routing_key=properties.reply_to, body=body)
        ch.basic_ack(delivery_tag=method.delivery_tag)

        if self.s3 is not None:
            if "asreview metrics" in cmd:
                # Extract the metrics.
                split_cmd = cmd.split()
                idx = split_cmd.index("-o")
                metrics_file = split_cmd[idx + 1]
                self.upload_to_s3(metrics_file, s3_prefix)

    def upload_to_s3(self, local_name, s3_prefix, s3_name=None):
        if s3_name is None:
            s3_name = local_name
        s3_name = s3_prefix + "/" + s3_name
        print(f"Uploading {local_name} to {s3_name}")
        self.s3_bucket.upload_file(local_name, s3_name)


if __name__ == "__main__":
    try:
        worker = Worker()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
