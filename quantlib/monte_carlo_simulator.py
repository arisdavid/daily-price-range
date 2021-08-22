import argparse
import logging
import math

import numpy as np
import numpy.matlib as ml
import redis
from decouple import config

logging.basicConfig(level=logging.INFO)


def init_redis():
    try:

        redis_host = config("REDIS_HOST")
        redis_port = config("REDIS_PORT")
        auth_pass = config("REDIS_AUTH_PASS")

        redis_client = redis.StrictRedis(
            host=redis_host, port=redis_port, password=auth_pass
        )
        redis_client.ping()
        logging.info("Redis connection ready.")

        return redis_client

    except Exception:
        logging.exception("Redis Cache not available")


def geometric_brownian_motion(
    starting_price, mu, sigma, num_trading_days, forecast_period, allow_negative=False
):

    """
    Geometric Brownian Motion
    Step 1 - Calculate the Deterministic component - drift
    Alternative drift 1 - supporting random walk theory
    drift = 0
    Alternative drift 2 -
    drift = risk_free_rate - (0.5 * sigma**2)
    :return: asset path
    """

    # Calculate Drift
    mu = mu / num_trading_days
    sigma = sigma / math.sqrt(num_trading_days)  # Daily volatility
    drift = mu - (0.5 * sigma ** 2)

    # Calculate Random Shock Component
    random_shock = np.random.normal(0, 1, (1, forecast_period))
    log_ret = drift + (sigma * random_shock)

    compounded_ret = np.cumsum(log_ret, axis=1)
    asset_path = starting_price + (starting_price * compounded_ret)

    # Include starting value
    starting_value = ml.repmat(starting_price, 1, 1)
    asset_path = np.concatenate((starting_value, asset_path), axis=1)

    if allow_negative:
        asset_path *= asset_path > 0

    return asset_path


def monte_carlo_simulation(
    num_sims, starting_price, mu, sigma, num_trading_days, forecast_period
):

    for n_sim in range(num_sims):
        yield geometric_brownian_motion(
            starting_price, mu, sigma, num_trading_days, forecast_period
        )


def main():

    parser = argparse.ArgumentParser("Monte Carlo Simulator")
    parser.add_argument("ticker", help="Ticker symbol", type=str)
    parser.add_argument("num_simulations", help="Number of simulations", type=int)
    parser.add_argument("starting_price", help="Starting value", type=float)
    parser.add_argument("mu", help="Expected annual return", type=float)
    parser.add_argument("sigma", help="Expected annual volatility", type=float)
    parser.add_argument("forecast_period", help="Forecast period in days", type=int)
    parser.add_argument(
        "num_trading_days", help="Number of trading days in year", type=int
    )

    args = parser.parse_args()
    asset_paths = monte_carlo_simulation(
        num_sims=args.num_simulations,
        starting_price=args.starting_price,
        mu=args.mu,
        sigma=args.sigma,
        num_trading_days=args.num_trading_days,
        forecast_period=args.forecast_period,
    )
    curve = []
    for asset_path in asset_paths:
        curve = +asset_path

    _redis_client = init_redis()
    try:
        # TODO: Check if key exists. Update if exists. Create if not exist.
        _redis_client.delete(args.ticker)
        _redis_client.hmset(
            args.ticker,
            {
                "min_price": curve.min(),
                "max_price": curve.max(),
                "mu": args.mu,
                "sigma": args.sigma,
            },
        )
        logging.info(f"Set redis value for key {args.ticker}")
    except Exception:
        logging.exception(f"Unable to cache {args.ticker}")

    return curve


if __name__ == "__main__":

    _curve = main()
