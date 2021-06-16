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

#Building ARIMA Model with a superstore dataset and find out the best configuration for forecasting sales

### 1.0 Loading Datasets
df = pd.read_excel("dataset/superstore.xls")
supplies = df.loc[df['Category'] == 'Office Supplies']

# ## 2.0 Data Preprocessing

supplies_sales = supplies.drop(columns=['Row ID', 'Order ID', 'Ship Date', 'Ship Mode', 'Customer ID', 'Customer Name', 
                                        'Segment', 'Country', 'City', 'State', 'Postal Code', 'Region', 'Product ID', 'Category'
                                        , 'Sub-Category', 'Product Name', 'Quantity', 'Discount', 'Profit'])

supplies_sales= supplies_sales.sort_values('Order Date')

supplies_sales = supplies_sales.groupby('Order Date')['Sales'].sum()
supplies_sales = supplies_sales.reset_index()

supplies_sales = supplies_sales.set_index('Order Date')

supplies_sales = supplies_sales['Sales'].resample('MS').mean()

# ## 3.0 Building Model

# ### 3.1 Fitting ARIMA Model
p = d = q = range(0, 2)
pdq = list(itertools.product(p, d, q))
seasonal_pdq = [(x[0], x[1], x[2], 12) for x in list(itertools.product(p, d, q))]

for param in pdq:
    for param_seasonal in seasonal_pdq:
        try:
            model_ARIMA = sm.tsa.statespace.SARIMAX(supplies_sales,
                                            order=param,
                                            seasonal_order=param_seasonal,
                                            enforce_stationarity=False,
                                            enforce_invertibility=False)
            #results = model_ARIMA.fit()
            #print('ARIMA{}x{}12 - AIC:{}'.format(param, param_seasonal, results.aic))
        except:
            continue

# As ARIMA(0, 1, 1)x(0, 1, 1, 12)12 has an AIC of 302.48, which is the lowest AIC. Therefore, we will take this as the optimal option.

model_ARIMA = sm.tsa.statespace.SARIMAX(supplies_sales,
                                order=(0, 1, 1),
                                seasonal_order=(0, 1, 1, 12),
                                enforce_invertibility=False)
results = model_ARIMA.fit()

# ### 3.2 Model Validation
pred = results.get_prediction(start=pd.to_datetime('2014-01-01'), dynamic=False)
pred_ci = pred.conf_int()
sales_forecasted = pred.predicted_mean
sales_truth = supplies_sales['2014-01-01':]

rmse = rmse(sales_truth,sales_forecasted)
mse = rmse**2

#Mean Squared Error of our the forecasts: 93416.08
#Root Mean Squared Error of the forecasts: 305.64

### Use this ARIMA Model for predicting sales of startup companies
#Forecasting for the next 12 months
def sales_prediction(df):
  
    #Predicting Sales

    #Fitting ARIMA Model
    #As ARIMA(0, 1, 1)x(0, 1, 1, 12)12 has the lowest AIC previously on sales dataset. Therefore, we will take this as the optimal option.
    model_ARIMA = sm.tsa.statespace.SARIMAX(df,
                                    order=(0, 1, 1),
                                    seasonal_order=(0, 1, 1, 12),
                                    enforce_invertibility=False)
    results = model_ARIMA.fit()

    #Save the Model

    pickle.dump(results, open('model_sales.pkl','wb'))

    #Load the Model

    model_sales = pickle.load(open('model_sales.pkl','rb'))

    return  model_sales.forecast(12).to_numpy()

def expenses_prediction(df):
  
    #Predicting Expenses
    #Fitting ARIMA Model
    model_ARIMA = sm.tsa.statespace.SARIMAX(df,
                                    order=(0, 1, 1),
                                    seasonal_order=(0, 1, 1, 12),
                                    enforce_invertibility=False)
    results = model_ARIMA.fit()

    #Save the Model

    pickle.dump(results, open('model_expenses.pkl','wb'))

    #Load the Model

    model_expenses = pickle.load(open('model_expenses.pkl','rb'))

    return  model_expenses.forecast(12).to_numpy()





