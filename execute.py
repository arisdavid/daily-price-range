import argparse
import logging
import uuid

from calc_stock_metric import StockMetrics
from k8s import Kubernetes

logging.getLogger().setLevel(logging.INFO)


class JobManager(Kubernetes):

    _num_trading_days = 250
    _num_sims = 10_000

    def __init__(self, ticker):
        super(JobManager, self).__init__()
        self.ticker = ticker
        stock = StockMetrics(self.ticker, "2020-08-20", "2021-08-20")
        self.sigma = str(stock.get_sigma())
        self.mu = str(stock.get_mu())
        self.starting_price = str(stock.get_close_price())

        # TODO: Remove hard-coding
        self.forecast_period = "1000"
        self.num_trading_days = str(self.num_trading_days)
        self.num_sims = str(self._num_sims)

    def create_job(self):

        image = "monte-carlo-simulator:latest"
        pull_policy = "Never"
        name = "montecarlosimulator"

        args = [
            self.num_sims,
            self.starting_price,
            self.mu,
            self.sigma,
            self.forecast_period,
            self.num_trading_days,
        ]

        pod_id = str(f"{self.ticker.lower()}-pod-{uuid.uuid4()}")
        container = self.make_container(image, name, pull_policy, args)
        pod_template = self.make_pod_template(pod_id, container)

        job_id = str(f"{self.ticker.lower()}-job-{uuid.uuid4()}")
        job = self.make_job(job_id, pod_template)

        logging.info(f"Created a job with job-id {job_id}")

        return job

    def execute(self):
        job = self.create_job()
        self.batch_api.create_namespaced_job(self._namespace, job)


if __name__ == "__main__":
    """ Usage: In shell or command line type: python -u execute.py -l AMZN AAPL MSFT"""
    parser = argparse.ArgumentParser("Job Manager")
    parser.add_argument(
        "-l",
        "--list",
        nargs="+",
        dest="tickers",
        help="List of ticker symbols",
        required=True,
    )
    _args = parser.parse_args()

    for _ticker in _args.tickers:
        logging.info(f"Processing {_ticker}")
        _job = JobManager(_ticker)
        _job.execute()
