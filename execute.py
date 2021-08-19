import argparse
import logging
import uuid

from k8s import Kubernetes

logging.getLogger().setLevel(logging.INFO)


class JobManager(Kubernetes):
    def __init__(self, ticker):
        super(JobManager, self).__init__()
        self.ticker = ticker

    def create_job(self):
        image = "monte-carlo-simulator:latest"
        pull_policy = "Never"
        name = "montecarlosimulator"

        num_sims = "1000"
        starting_price = "100"
        mu = "0.2"
        sigma = "0.2"
        forecast_period = "250"
        num_trading_days = "250"
        args = [num_sims, starting_price, mu, sigma, forecast_period, num_trading_days]

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
    """ Usage: In shell or command line type: python -u execute.py <ticker_symbol>"""
    parser = argparse.ArgumentParser("Job Manager")
    parser.add_argument("input_ticker", help="Input Ticker Symbol", type=str)
    _args = parser.parse_args()

    job = JobManager(_args.input_ticker)
    job.execute()
