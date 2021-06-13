import itertools
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pickle
import scipy
import statsmodels
import sklearn
import statsmodels.api as sm
from statsmodels.tsa.seasonal import seasonal_decompose 
from statsmodels.tools.eval_measures import rmse
import warnings
warnings.filterwarnings("ignore")

def model_prediction(df):
  
    # ## 3.0 Building Model

    # ### 3.1 Fitting ARIMA Model
    p = d = q = range(0, 2)
    pdq = list(itertools.product(p, d, q))
    seasonal_pdq = [(x[0], x[1], x[2], 12) for x in list(itertools.product(p, d, q))]

    for param in pdq:
        for param_seasonal in seasonal_pdq:
            try:
                model_ARIMA = sm.tsa.statespace.SARIMAX(df,
                                                order=param,
                                                seasonal_order=param_seasonal,
                                                enforce_stationarity=False,
                                                enforce_invertibility=False)
                results = model_ARIMA.fit()
            except:
                continue

    model_ARIMA = sm.tsa.statespace.SARIMAX(df,
                                    order=(0, 1, 1),
                                    seasonal_order=(0, 1, 1, 12),
                                    enforce_invertibility=False)
    results = model_ARIMA.fit()

    # ## 5.0 Save the Model

    pickle.dump(results, open('model.pkl','wb'))

    # ## 6.0 Load the Model

    model = pickle.load(open('model.pkl','rb'))

    return  model.forecast(12).to_numpy()




