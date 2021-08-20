# Daily Price Range (Mean-Reversion Strategy)

Work In Progress.

### Introduction
```execute.py``` will interact with Kubernetes API to launch ephemeral pods to 
perform monte carlo simulation using ```Geometric Brownian Motion (GBM)``` model to predict the stock's "expected" range - lower and upper bounds.

It will cache the results in Redis. 

### Prerequisites
1. Create a virtual environment to install python packages from requirement.txt
2. ``` make dev-configure ```
3. ``` make build ``` . If using minikube as k8s cluster make sure to run ``` eval $(minikube docker-env) ``` before building the docker file
    
4. ``` make install-redis ```

#### Example
One stock
```.shell script
python -u execute.py -l AAPL
```

Multiple stocks
```.shell script
python -u execute.py -l AAPL AMZN MSFT GOOG CRWD UPST HOOD
```


---
### Geometric Brownian Motion

Geometric Brownian Motion is the model used. This model is used in Finance to model Stock prices. 
GBM says the change in stock price is the stock price "S" multiplied by the two terms; drift and shock.

![Image of GBM](https://github.com/arisdavid/daily-price-range/blob/master/documentation/img/eq.png)

The first term is a ```drift``` (deterministic component) and the second term is a ```shock.``` (random shock). 
For each time period, our model assumes the price will "drift" up by the expected return. 
But the drift will be shocked (added or subtracted) by a random shock. 
The random shock will be the standard deviation "s" multiplied by a random number "e." 
This is simply a way of scaling the standard deviation

