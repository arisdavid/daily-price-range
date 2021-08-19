# Daily Price Range (Mean-Reversion Strategy)

###
```execute.py``` will interact with Kubernetes API to launch ephemeral pods to 
perform ```Geometric Brownian Motion (GBM)``` calculation to predict the stock's "expected" range - lower and upper bounds.

### Examples
```.shell script
python -u execute.py "AMZN"
```

### Financial Model 

Geometric Brownian Motion. This model is widely applied in Finance to model Stock prices. 
GBM says the change in stock price is the stock price "S" multiplied by the two terms.

![Image of GBM](https://github.com/arisdavid/daily-price-range/blob/master/documentation/img/eq.png)

The first term is a ```drift``` (deterministic component) and the second term is a ```shock.``` (random shock) 
For each time period, our model assumes the price will "drift" up by the expected return. 
But the drift will be shocked (added or subtracted) by a random shock. 
The random shock will be the standard deviation "s" multiplied by a random number "e." 
This is simply a way of scaling the standard deviation

