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


### 1.0 Loading Datasets
df = pd.read_excel("superstore.xls")
supplies = df.loc[df['Category'] == 'Office Supplies']

# ## 2.0 Data Preprocessing

supplies_sales = supplies.drop(columns=['Row ID', 'Order ID', 'Ship Date', 'Ship Mode', 'Customer ID', 'Customer Name', 
                                        'Segment', 'Country', 'City', 'State', 'Postal Code', 'Region', 'Product ID', 'Category'
                                        , 'Sub-Category', 'Product Name', 'Quantity', 'Discount', 'Profit'])

supplies_sales= supplies_sales.sort_values('Order Date')
supplies_sales.isnull().sum()

supplies_sales = supplies_sales.groupby('Order Date')['Sales'].sum()
supplies_sales = supplies_sales.reset_index()

supplies_sales = supplies_sales.set_index('Order Date')

supplies_sales = supplies_sales['Sales'].resample('MS').mean()

supplies_sales.plot(figsize=(15, 10))
plt.show()

decomposition = seasonal_decompose(supplies_sales, model = "add")
plt.figure(figsize = (15,10))
decomposition.plot();

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
            results = model_ARIMA.fit()
            print('ARIMA{}x{}12 - AIC:{}'.format(param, param_seasonal, results.aic))
        except:
            continue


# As ARIMA(0, 1, 1)x(0, 1, 1, 12)12 has an AIC of 302.48, which is the lowest AIC. Therefore, we will take this as the optimal option.

model_ARIMA = sm.tsa.statespace.SARIMAX(supplies_sales,
                                order=(0, 1, 1),
                                seasonal_order=(0, 1, 1, 12),
                                enforce_invertibility=False)
results = model_ARIMA.fit()
print(results.summary().tables[1])

results.plot_diagnostics(figsize=(20, 15))
plt.show()

# ### 3.2 Model Validation

pred = results.get_prediction(start=pd.to_datetime('2014-01-01'), dynamic=False)
pred_ci = pred.conf_int()
ax = supplies_sales['2014':].plot(label='Observed')
pred.predicted_mean.plot(ax=ax, label='Forecast', alpha=.9, figsize=(14, 7))
ax.set_xlabel('Date')
ax.set_ylabel('Supplies Sales')
plt.legend()
plt.show()

sales_forecasted = pred.predicted_mean
sales_truth = supplies_sales['2014-01-01':]

rmse = rmse(sales_truth,sales_forecasted)
mse = rmse**2

print('The Mean Squared Error of our forecasts is', mse)
print('The Root Mean Squared Error of our forecasts is', rmse)

# ## 4.0 Forecasting Sales

pred_uc = results.get_forecast(steps=50)
pred_ci = pred_uc.conf_int()
ax = supplies_sales.plot(label='observed', figsize=(14, 7))
pred_uc.predicted_mean.plot(ax=ax, label='Forecast')
ax.fill_between(pred_ci.index,
                pred_ci.iloc[:, 0],
                pred_ci.iloc[:, 1], color='red', alpha=.1)
ax.set_xlabel('Date')
ax.set_ylabel('Supplies Sales')
plt.legend()
plt.show()

# ## 5.0 Save the Model

pickle.dump(results, open('model.pkl','wb'))

# ## 6.0 Load the Model

model = pickle.load(open('model.pkl','rb'))

###Testing

arr = np.array([103, 85, 204, 333, 107,33,444,123,152,532,223,464])
df = pd.DataFrame(arr)

model_ARIMA = sm.tsa.statespace.SARIMAX(df,
                                            order=param,
                                            seasonal_order=param_seasonal,
                                            enforce_stationarity=False,
                                            enforce_invertibility=False)
test = model_ARIMA.fit()

pred = results.get_prediction(dynamic=False)
pred_ci = pred.conf_int()
ax = df.plot(label='Observed')
pred.predicted_mean.plot(ax=ax, label='Forecast', alpha=.9, figsize=(14, 7))
ax.set_xlabel('Month')
ax.set_ylabel('Supplies Sales')
plt.legend()
plt.show()

#Forecast 1 year later
pred_uc = test.get_forecast(steps=12)
pred_ci = pred_uc.conf_int()
ax = df.plot(label='observed', figsize=(14, 7))
pred_uc.predicted_mean.plot(ax=ax, label='Forecast')
ax.set_xlabel('Month')
ax.set_ylabel('Supplies Sales')
plt.legend()
plt.show()


