import argparse
import logging

from quantlib import monte_carlo_simulator
from quantlib.calc_stock_metric import StockMetrics

logging.getLogger().setLevel(logging.INFO)


def run_monte_carlo_simulator(args):
    num_trading_days = 250
    forecast_period = 250

    stock = StockMetrics(args.input_ticker, "2020-08-19", "2021-08-19")
    mu = stock.get_mu()
    sigma = stock.get_sigma()

    asset_path = monte_carlo_simulator.geometric_brownian_motion(
        100, mu, sigma, num_trading_days, forecast_period
    )
    return asset_path


if __name__ == "__main__":
    """ Usage: In shell or command line type: python -u execute.py <ticker_symbol>"""
    parser = argparse.ArgumentParser("Job Executor")
    parser.add_argument("input_ticker", help="Input Ticker Symbol", type=str)
    _args = parser.parse_args()
    _asset_path = run_monte_carlo_simulator(_args)

    logging.info("Predicted price path")
    logging.info(_asset_path)
