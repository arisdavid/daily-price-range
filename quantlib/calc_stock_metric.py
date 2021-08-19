import logging

import yfinance as yf

logging.getLogger().setLevel(logging.INFO)


class StockMetrics:
    def __init__(self, ticker, from_date, to_date):
        self.ticker = ticker
        self.from_date = from_date
        self.to_date = to_date
        self._hist_price = self._download_historical_price()
        self._mu, self._sigma = self._calc_metrics()

    def _download_historical_price(self):

        hist_record = yf.download(self.ticker, self.from_date, self.to_date)

        if hist_record.empty:
            raise Exception(
                f"Unable to download historical record for ticker {self.ticker} "
                f"{self.ticker} from {self.from_date} to {self.to_date}"
            )
        else:
            logging.info(
                f"Downloaded historical record for "
                f"{self.ticker} from {self.from_date} to {self.to_date}"
            )
            return hist_record

    def _calc_metrics(self):

        """ Calculate volatility (sigma) and expected return (mu) """
        mu = self._hist_price["Adj Close"].pct_change().mean()
        sigma = self._hist_price["Adj Close"].pct_change().std()

        return mu, sigma

    def get_mu(self):
        return self._mu

    def get_sigma(self):
        return self._sigma
