#!/usr/bin/env python
import os
import sys

import pika

RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.environ.get("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.environ.get("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.environ.get("RABBITMQ_PASS", "guest")


class Tasker(object):
    def __init__(self, filename):
        if not os.path.exists(filename):
            print(f"Error: File {filename} does not exist")
            exit(1)
        print(f"Logging as {RABBITMQ_USER}")

        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
        parameters = pika.ConnectionParameters(
            RABBITMQ_HOST,
            RABBITMQ_PORT,
            "/",
            credentials,
            heartbeat=3600,
        )

        self.connection = pika.BlockingConnection(parameters)
        channel = self.connection.channel()

        channel.queue_declare(queue="tasker")
        channel.queue_declare(queue="asreview_queue", durable=True)

        self.sent_messages = 0

        print(f"Sending file {filename}")
        with open(filename, encoding="utf-8") as f:
            lines = f.readlines()
            for i, message in enumerate(lines):
                print(f"Sent [{i}]: {message}")
                channel.basic_publish(
                    exchange="",
                    routing_key="asreview_queue",
                    body=message,
                    properties=pika.BasicProperties(
                        delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE,
                        reply_to="tasker",
                    ),
                )
                self.sent_messages += 1

        channel.basic_consume(
            "tasker", on_message_callback=self.callback, auto_ack=True
        )
        channel.start_consuming()

    def callback(self, ch, method, properties, body):
        print(f"[{self.sent_messages} Done] Msg: {body.decode()}")
        self.sent_messages -= 1
        if self.sent_messages == 0:
            self.connection.close()
            sys.exit(0)


if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
            print("Usage:\npython {sys.argv[0]} FILENAME\n")
            exit(1)

        filename = sys.argv[1]
        tasker = Tasker(filename)
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
