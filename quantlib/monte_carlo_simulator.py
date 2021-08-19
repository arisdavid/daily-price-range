import logging
import math

import numpy as np
import numpy.matlib as ml

logging.basicConfig(level=logging.INFO)


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

    return asset_path.mean(axis=0)
