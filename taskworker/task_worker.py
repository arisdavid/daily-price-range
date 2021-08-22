import logging
import os
import uuid
from datetime import date, timedelta

import pika
from calc_stock_metric import StockMetrics
from decouple import config
from k8s import Kubernetes

logging.basicConfig(level=logging.INFO)
logging.getLogger("pika").setLevel(logging.WARNING)


class JobManager(Kubernetes):

    _num_trading_days = 250
    _num_sims = 10_000
    _forecast_period = 250

    _to_date_py = date.today()
    _from_date_py = _to_date_py - timedelta(20)

    _to_date = _to_date_py.strftime("%Y-%m-%d")
    _from_date_py = _from_date_py.strftime("%Y-%m-%d")

    _image = "monte-carlo-simulator:latest"
    _pull_policy = "Never"
    _name = "montecarlosimulator"

    def __init__(self, ticker):
        super(JobManager, self).__init__()
        self.ticker = ticker
        stock = StockMetrics(self.ticker, self._from_date_py, self._to_date)
        self.sigma = str(stock.get_sigma())
        self.mu = str(stock.get_mu())
        self.starting_price = str(stock.get_close_price())
        self.forecast_period = str(self._forecast_period)
        self.num_trading_days = str(self._num_trading_days)
        self.num_sims = str(self._num_sims)

    def create_job(self):
        image = self._image
        name = self._name
        pull_policy = self._pull_policy

        args = [
            self.ticker,
            self.num_sims,
            self.starting_price,
            self.mu,
            self.sigma,
            self.forecast_period,
            self.num_trading_days,
        ]

        job_id = str(f"{self.ticker.lower()}-{uuid.uuid4()}")
        container = self.make_container(image, name, pull_policy, args)
        pod_template = self.make_pod_template(job_id, container)
        job = self.make_job(job_id, pod_template)

        logging.info(f"Created a job with job-id {job_id}")

        return job

    def execute(self):
        job = self.create_job()
        self.batch_api.create_namespaced_job(self._namespace, job)


def read_message():
    credentials = pika.PlainCredentials(config("RMQ_USERNAME"), config("RMQ_PASSWORD"))
    conn = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=config("RMQ_HOST"), port=config("RMQ_PORT"), credentials=credentials,
        )
    )
    channel = conn.channel()
    channel.queue_declare(queue="trading-queue", durable=True)

    def message_callback(ch, method, properties, body):
        logging.info(f"Performing quantitative analysis on {body}")
        job = JobManager(body.decode("utf-8"))
        job.execute()
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue="trading-queue", on_message_callback=message_callback)
    channel.start_consuming()
    conn.close()


if __name__ == "__main__":
    logging.info(os.environ)
    read_message()
