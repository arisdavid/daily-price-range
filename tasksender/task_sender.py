import argparse
import logging

import pika
from decouple import config

logging.basicConfig(level=logging.INFO)
logging.getLogger("pika").setLevel(logging.WARNING)


def send_task(task):
    credentials = pika.PlainCredentials(config("RMQ_USERNAME"), config("RMQ_PASSWORD"))
    conn = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=config("RMQ_HOST"), port=config("RMQ_PORT"), credentials=credentials,
        )
    )
    channel = conn.channel()
    channel.queue_declare(queue="trading-queue", durable=True)
    channel.basic_publish(
        exchange="",
        routing_key="trading-queue",
        body=task,
        properties=pika.BasicProperties(delivery_mode=2),
    )
    logging.info(f"Sent {task} to be processed.")
    conn.close()


if __name__ == "__main__":
    """Usage: In shell or command line type: python -u task_sender.py -l AMZN AAPL MSFT"""
    parser = argparse.ArgumentParser("Job Manager")
    parser.add_argument(
        "-l" "--list",
        nargs="+",
        dest="tickers",
        help="List of ticker symbols",
        required=True,
    )
    _args = parser.parse_args()

    for _ticker in _args.tickers:
        logging.info(f"Processing {_ticker}")
        send_task(_ticker)
