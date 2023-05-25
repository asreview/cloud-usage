#!/usr/bin/env python
import os
import shutil
import subprocess
import sys

import pika

RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.environ.get("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.environ.get("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.environ.get("RABBITMQ_PASS", "guest")


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

        print("[*] Waiting for messages. CTRL+C to exit")
        channel.start_consuming()

    def callback(self, ch, method, properties, body):
        cmd = body.decode()
        print("=> Received %r" % cmd)
        try:
            subprocess.run(
                cmd,
                check=True,
                shell=True,
            )

            print("✓ Done")
            ch.basic_publish("", routing_key=properties.reply_to, body=body)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as err:
            if "simulate" in cmd:
                split_cmd = cmd.split()
                idx = split_cmd.index("-s")
                filename = split_cmd[idx + 1]
                shutil.rmtree(f"{filename}.tmp")

                with open(f"issues/{RABBITMQ_USER}.txt", "a", encoding="utf-8") as f:
                    f.write(cmd)
                print("x Error on simulate, deleting tmp file, storing file on issues/")
                ch.basic_publish("", routing_key=properties.reply_to, body=body)
                ch.basic_ack(delivery_tag=method.delivery_tag)
            else:
                raise err

if __name__ == "__main__":
    try:
        worker = Worker()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
